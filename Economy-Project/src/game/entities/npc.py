from random import randint

class NPC:
    def __init__(self, name, dialogue, x, y):
        self.name = name
        self.dialogue = dialogue
        self.x = x
        self.y = y

    def speak(self):
        return f"{self.name}: {self.dialogue[randint(0, len(self.dialogue) - 1)]}"

    def get_position(self):
        return self.x, self.y

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def interact(self):
        return f"Interactuaste con {self.name}!"