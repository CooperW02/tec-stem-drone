import pygame
from time import sleep

pygame.init()
pygame.joystick.init()

controller = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joy in controller:
    joy.init()


buttons = {
    'x': 0, 'o': 0, 't': 0, 's': 0, 'share': 0, 'ps': 0, 'options': 0, 'L3': 0, 'R3': 0,
    'L1': 0, 'R1': 0, 'dpad_up': 0, 'dpad_down': 0, 'dpad_left': 0, 'dpad_right': 0, 'touchpad': 0
}
axiss = [0.0] * 10  # Adjust size if necessary

def getJS(name=''):
    global buttons
    # retrieve any events ..
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            axiss[event.axis] = round(event.value, 1)
            # print(f"Axis {event.axis} moved to {event.value}")

        elif event.type == pygame.JOYBUTTONDOWN:
            print(event)
            for x, (key, val) in enumerate(buttons.items()):
                if x < 16:
                    if controller[0].get_button(x):
                        buttons[key] = 1
                        # print(f"Button {key} pressed")

        elif event.type == pygame.JOYBUTTONUP:
            print(event)
            for x, (key, val) in enumerate(buttons.items()):
                if x < 16:
                    if event.button == x:
                        buttons[key] = 0
                        # print(f"Button {key} released")

        elif event.type == pygame.JOYHATMOTION:
            hat_value = controller[0].get_hat(0)
            buttons['dpad_up'] = 1 if hat_value[1] == 1 else 0
            buttons['dpad_down'] = 1 if hat_value[1] == -1 else 0
            buttons['dpad_left'] = 1 if hat_value[0] == -1 else 0
            buttons['dpad_right'] = 1 if hat_value[0] == 1 else 0
            print(f"Hat moved to {hat_value}")

    # Update dictionary with axis values
    buttons['left_stick_x'], buttons['left_stick_y'] = axiss[0], axiss[1]
    buttons['right_stick_x'], buttons['right_stick_y'] = axiss[2], axiss[3]
    buttons['L2_axis'], buttons['R2_axis'] = axiss[4], axiss[5]

    if name == '':
        return buttons
    else:
        return buttons[name]

def main():
    '''Print to get Single Value Only'''
    getJS()
    sleep(0.05)

if __name__ == "__main__":
    while True:
        main()