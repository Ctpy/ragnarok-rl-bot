import os
import pickle


class Monster:
    def __init__(self, name, image_data):
        self.name = name
        self.image_data = image_data


def save_monster_to_file(monster, filename):
    with open(filename, 'wb') as file:
        pickle.dump(monster, file)


def load_monster_object(filename) -> Monster:
    with open(filename, 'rb') as file:
        monster = pickle.load(file)
    return monster
