import cv2, imutils, socket
from djitellopy import Tello
import threading
import socket
import time
import PS4Joystick as js
from pynput.keyboard import Key, Listener
from pynput import keyboard
import numpy as np
import base64

from time import sleep
from pynput import keyboard

me = Tello()
me.connect()

controller = False
global returnmsg
returnmsg = ''

BUFF_SIZE = 65536
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

ip = "0.0.0.0"
port = 11111
# s.bind((ip,port))

movement = 'Joystick'
kb_in = None

dic = {
    'w': 0, 's': 0, 'a': 0, 'd': 0, 'left': 0, 'right': 0, 'up': 0, 'down': 0, 'q': 0, 'e': 0, 'esc': 0
}

commands = ["command", "takeoff", "land", "streamon", "streamoff", "emergency", "up", "down", "left", "right", "forward", "back",
            "cw", "ccw", "flip", "go", "stop", "curve", "jump", "speed", "rc", "wifi", "mon", "moff", "mdirection", "ap", "speed?",
            "battery?", "time?", "wifi?", "sdk?", "sn?", "sequence", "end", "stats", "keyboard", "controller_on", "opencam", "controller_off"]

def recv1():
    while True:
        packet, _ = s.recvfrom(BUFF_SIZE)
        data = base64.b64decode(packet, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        cv2.imshow("sender", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            s.close()
            break


host = ''
port = 9000
locaddr = (host, port)
stats = {'speed': 0, 'battery': 0, 'time': 0, 'wifi': '', 'sdk': '', 'sn': ''}

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

x1 = threading.Thread(target=recv1)


def recv():
    while True:
        try:
            data, server = sock.recvfrom(1518)
            print(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break


print('\r\n\r\nTello Python3 Demo.\r\n')

print('Tello: command takeoff land flip forward back left right \r\n       up down cw ccw speed speed? sequence\r\n')

print('end -- quit demo.\r\n')

# recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()


def controller_input():
    print("Controller input on \n")
    while True:
        vals = move()
        if vals == "off":
            print("Controller input off")
            break
        # print(vals)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])


def move():
    flag = 0
    if movement == 'Joystick':
        jsVal = js.getJS()
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 70

        if flag == 0:
            if (jsVal['o']) == 1:
                # me.takeoff()
                print("Take off")
                sleep(1)
                flag = 1

        if (jsVal['t']) == 1:
            # me.land()
            print("Land")
            flag = 0
            sleep(1)

        dpad_directions = {
            (0, 1): 'dpad_up',
            (0, -1): 'dpad_down',
            (-1, 0): 'dpad_left',
            (1, 0): 'dpad_right',
            (-1, 1): 'dpad_up_left',
            (1, 1): 'dpad_up_right',
            (-1, -1): 'dpad_down_left',
            (1, -1): 'dpad_down_right',
            (0, 0): 'dpad_centered'
        }

        hat_value = (
            int(jsVal['dpad_right']) - int(jsVal['dpad_left']),
            int(jsVal['dpad_up']) - int(jsVal['dpad_down'])
        )
        dpad_direction = dpad_directions.get(hat_value, 'unknown')

        if dpad_direction == 'dpad_up':
            # print('dpad up')
            me.flip_forward()
        elif dpad_direction == 'dpad_down':
            # print('dpad down')
            me.flip_back()
        elif dpad_direction == 'dpad_left':
            # print('dpad left')
            me.flip_left()
        elif dpad_direction == 'dpad_right':
            # print('dpad right')
            me.flip_right()

        if (jsVal['ps']) == 1:
            return "off"

        if (jsVal['left_stick_x']) == 1:
            lr = speed  #"right"

        elif (jsVal['left_stick_x']) == -1.0:
            lr = -speed  #"left"

        if (jsVal['left_stick_y']) == 1:
            fb = -speed  #"backward"

        elif (jsVal['left_stick_y']) == -1.0:
            fb = speed  #"forward"

        if (jsVal['right_stick_x']) == 1:
            yv = speed  #"pitchright"

        elif (jsVal['right_stick_x']) == -1.0:
            yv = -speed  #"pitchleft"

        if (jsVal['right_stick_y']) == 1:
            ud = -speed  #"down"

        elif (jsVal['right_stick_y']) == -1.0:
            ud = speed  #"up"

        if (jsVal['left_stick_x']) != 1 and (jsVal['left_stick_x']) != -1 and (jsVal['left_stick_y']) != 1 and (
        jsVal['left_stick_y']) != -1 and (jsVal['right_stick_x']) != 1 and (jsVal['right_stick_x']) != -1 and (
        jsVal['right_stick_y']) != 1 and (jsVal['right_stick_y']) != -1:
            lr, fb, ud, yv = 0, 0, 0, 0

        return [lr, fb, ud, yv]



while True:

    try:
        msg = input("")
        msg = msg.lower()
        cmd = msg.split(' ')

        if not msg:
            break

        if 'end' == cmd[0]:
            print('...')
            sock.close()
            break

        if 'sequence' == cmd[0]:
            if len(cmd) == 2:
                sequence_number = cmd[1]
                if sequence_number.isnumeric():
                    sequence_number = cmd[1]
                    sequence_number = int(sequence_number)
                    print(f'\r\nTest sequence {sequence_number} activated')
                    sequence1 = ['takeoff', 'cw 360', 'ccw 360', 'forward 50', 'back 50', 'left 50', 'right 50', 'land']
                    sequence2 = ['takeoff', 'land']
                    sequence3 = ['takeoff', 'forward 50', 'flip f', 'left 50', 'up 50', 'down 50', 'right 50',
                                 'back 50', 'land']
                    sequence4 = ['', '', '', '', '', '', '', '', '', '', '']
                    d = ["sequence1", "sequence2", "sequence 3"]
                    if f'sequence{sequence_number}' in locals():
                        sequence = vars()[f"sequence{sequence_number}"]
                        for x in sequence:
                            msg = x.encode(encoding="utf-8")
                            sock.sendto(msg, tello_address)
                            time.sleep(5)
                        print(f'Test sequence {sequence_number} successfully finished\n')
                    else:
                        print(f"\nSequence does not exist. Current setup sequences: \n", *d, sep=" ")
                        print("\n")
                else:
                    print("\nIncorrect Syntax. \n sequence (number)\n")
            elif len(cmd) > 2:
                print("\nIncorrect Syntax. Too many args\n")
            elif len(cmd) <= 1:
                print("\nIncorrect Syntax. Needs at least 2 args\n")
        elif 'stats' == cmd[0]:
            stats['speed'] = sock.sendto(b'speed?', tello_address)
            stats['battery'] = sock.sendto(b'battery?', tello_address)
            stats['time'] = sock.sendto(b'time?', tello_address)
            stats['wifi'] = sock.sendto(b'wifi?', tello_address)
            stats['sdk'] = sock.sendto(b'sdk?', tello_address)
            stats['sn'] = sock.sendto(b'sn?', tello_address)
            print(
                f'\nSpeed: {stats["speed"]} Battery: {stats["battery"]} Time: {stats["time"]} Wifi: {stats["wifi"]} Sdk: {stats["sdk"]} Sn: {stats["sn"]} \n')
        elif 'keyboard' == cmd[0]:

            def kb_send(dic):
                global kb_in
                lr, fb, ud, yv = 0, 0, 0, 0

                speed = 80
                liftSpeed = 80
                moveSpeed = 85
                rotationSpeed = 100

                if dic['left'] == 1:
                    lr = -speed  # Controlling The Left And Right Movement
                    print("Key left")
                elif dic['right'] == 1:
                    lr = speed
                    print("Key right")

                if dic['up'] == 1:
                    fb = moveSpeed  # Controlling The Front And Back Movement
                    print("Key up")
                elif dic['down'] == 1:
                    fb = -moveSpeed
                    print("Key down")

                if dic['w'] == 1:
                    ud = liftSpeed  # Controlling The Up And Down Movemnt:
                    print("Key w")
                elif dic['s'] == 1:
                    ud = -liftSpeed
                    print("Key s")

                if dic['d'] == 1:
                    yv = rotationSpeed  # Controlling the Rotation:
                    print("Key d")
                elif dic['a'] == 1:
                    yv = -rotationSpeed
                    print("Key a")

                if dic['q'] == 1:
                    sock.sendto(b'land', tello_address);
                    time.sleep(3)  # Landing The Drone
                    me.land()
                    print("Key q")
                elif dic['e'] == 1:
                    # sock.sendto(b'takeoff', tello_address)  # Take Off The Drone
                    me.takeoff()
                    print("Key e")

                if dic['esc'] == 1:
                    kb_in = "off"
                else:
                    kb_in = [lr, fb, ud, yv]  # Return The Given Value


            def on_press(key):
                try:
                    if key.char in dic:
                        dic[key.char] = 1
                except AttributeError:
                    if key == keyboard.Key.esc:
                        dic['esc'] = 1
                    elif key == keyboard.Key.left:
                        dic['left'] = 1
                    elif key == keyboard.Key.right:
                        dic['right'] = 1
                    elif key == keyboard.Key.up:
                        dic['up'] = 1
                    elif key == keyboard.Key.down:
                        dic['down'] = 1


            def on_release(key):
                try:
                    if key.char in dic:
                        dic[key.char] = 0
                except AttributeError:
                    if key == keyboard.Key.esc:
                        dic['esc'] = 0
                    elif key == keyboard.Key.left:
                        dic['left'] = 0
                    elif key == keyboard.Key.right:
                        dic['right'] = 0
                    elif key == keyboard.Key.up:
                        dic['up'] = 0
                    elif key == keyboard.Key.down:
                        dic['down'] = 0


            def keyboard_listener():
                with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                    listener.join()


            listener_thread = threading.Thread(target=keyboard_listener)
            listener_thread.start()

            while True:

                kb_send(dic)

                if kb_in == "off":
                    print("keyboard off")
                    keyboard.Listener.stop()
                    break
                else:
                    #kb = "rc {} {} {} {}".format(kb_in[0], kb_in[1], kb_in[2], kb_in[3])
                    # kb = kb.encode(encoding="utf-8")
                    # kb_sent = sock.sendto(kb, tello_address)
                    me.send_rc_control(kb_in[0], kb_in[1], kb_in[2], kb_in[3])
                    # print(kb_in)
            # LEFT RIGHT, FRONT BACK, UP DOWN, YAW VELOCITY

        elif 'opencam' == cmd[0]:
            x1.start()\

        elif 'controller_on' == cmd[0]:
            controller = True
            controller_input()
        elif 'controller_off' == cmd[0]:
            print("controller off")
            controller = False
        else:
            if cmd[0] in commands:

                # Send data
                msg = msg.encode(encoding="utf-8")
                sent = sock.sendto(msg, tello_address)
            else:
                print(f"Command not recognised. Possible commands: \n ", *commands, sep=" ")
    except KeyboardInterrupt:
        print('\n . . .\n')
        sock.close()
        break
