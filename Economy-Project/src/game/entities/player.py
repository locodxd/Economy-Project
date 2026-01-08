from random import randint

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.level = 1
        self.experience = 0
        self.inventory = []
        self.coins = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > 100:
            self.health = 100

    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level_up()

    def level_up(self):
        self.level += 1
        self.health = 100  # Restore health on level up
        print(f"{self.name} leveled up to level {self.level}!")

    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def earn_coins(self, amount):
        self.coins += amount

    def spend_coins(self, amount):
        if amount <= self.coins:
            self.coins -= amount
        else:
            print("no tienes suficientes monedas brother")