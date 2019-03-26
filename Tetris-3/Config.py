from abc import ABC
import json


class Config(ABC):
    I = [(0,0), (1,0), (2,0), (3,0)]
    O = [(0, 0), (1, 0), (0, 1), (1, 1)]
    T = [(0, 0), (0, 1), (1, 1), (0, 2)]
    L = [(0, 0), (1, 0), (0, 1), (0, 2)]
    J = [(0, 0), (0, 1), (0, 2), (1, 2)]
    Z = [(0, 0), (0, 1), (1, 1), (1, 2)]
    S = [(1, 0), (0, 1), (1, 1), (0, 2)]
    TETRI_LIST = [I, O, T, L, J, Z, S]
    
    COLORS = ['gray7', 'hot pink', 'turquoise1', 'maroon1', 'green2', 'purple1', 'gold', 'snow'] # Différentes couleurs utilisé : 1 => Background | 2 - 7 => Coleurs de tetri
    COMPLETE_QUOTES = ['Ligne complétée !', 'Double !', 'TRIPLE !', 'TETRIS !', 'BACK TO BACK TETRIS'] # Phrases écritent à l'écran lorsqu'une action est effectué 

    # ------ TOUCHES DE JEU ------ #
    # Liste des codes de touche et respectivement la correspondance de celle ci
    HOTKEYS = [81, 68, 90, 32, 83, 0, 27]
    HOTKEYS_LABEL = ["Gauche", "Droite", "Rotation", "Hard drop", "Soft drop", "Hold", "Pause"]

    # ------ DIFFICULTES ------ #
    BASE_DIFFICULTIES = [450, 400, 375, 350, 300]
    DIFFICULTE = 2
    SPEED = BASE_DIFFICULTIES[DIFFICULTE] # Correspond au temps (ms) entre chaque itération de la boucle update

    # ------ CONFIGURATION GLOBALE ------ #
    GRID_HEIGHT = 16
    GRID_WIDTH = 10
    PIXEL_SIZE = 40
    CANVAS_HEIGHT = PIXEL_SIZE * GRID_HEIGHT
    CANVAS_WIDTH = PIXEL_SIZE * GRID_WIDTH

    @staticmethod
    def toString():
        response = f'Difficulté : {Config.DIFFICULTE} \nVitesse initiale : {Config.SPEED} \nTaille d\'un carré : {Config.PIXEL_SIZE} \n'
        for i, value in enumerate(Config.HOTKEYS):
            response = response + f'Touche [{Config.HOTKEYS_LABEL[i]}] : {value} \n'
        return response

    @staticmethod
    def save():
        save = {
            Config.HOTKEYS_LABEL[0] : Config.HOTKEYS[0],
            Config.HOTKEYS_LABEL[1] : Config.HOTKEYS[1],
            Config.HOTKEYS_LABEL[2] : Config.HOTKEYS[2],
            Config.HOTKEYS_LABEL[3] : Config.HOTKEYS[3],
            Config.HOTKEYS_LABEL[4] : Config.HOTKEYS[4],
            Config.HOTKEYS_LABEL[5] : Config.HOTKEYS[5],
            'Difficulte' : Config.DIFFICULTE
        }
        with open('config.json', 'w') as f:
            json.dump(save, f, sort_keys=True, indent=4)

    @staticmethod
    def load():
        load = dict()
        with open('config.json', 'r') as f:
            load = json.load(f)
        try:
            for i in range(len(Config.HOTKEYS)):
                Config.HOTKEYS[i] = load[Config.HOTKEYS_LABEL[i]]
            Config.DIFFICULTE = load['Difficulte']
        except KeyError:
            Config.save()
