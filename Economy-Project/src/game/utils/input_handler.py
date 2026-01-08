from pygame import KEYDOWN, KEYUP, K_ESCAPE, K_RETURN, K_UP, K_DOWN, K_LEFT, K_RIGHT

class InputHandler:
    def __init__(self):
        self.keys = {}
        self.mouse_buttons = {}
        self.mouse_position = (0, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                self.keys[event.key] = True
            elif event.type == KEYUP:
                self.keys[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[event.button] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button] = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_position = event.pos

    def is_key_pressed(self, key):
        return self.keys.get(key, False)

    def is_mouse_button_pressed(self, button):
        return self.mouse_buttons.get(button, False)

    def get_mouse_position(self):
        return self.mouse_position

    def reset(self):
        self.keys.clear()
        self.mouse_buttons.clear()