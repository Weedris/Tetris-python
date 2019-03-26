from random import choice
from tkinter import Tk, Canvas, Label, StringVar, Toplevel, Button
from tkinter.messagebox import askretrycancel
from Config import Config
from ConfigWindow import ConfigWindow
from Tetrimino import Tetrimino
import os, sys
import pygame


class Tetris:
    def __init__(self):
        Config.load()

        self.master = Tk()
        self.master.title("Tetris")
        self.master.configure(background='grey25')

        # Fenêtre de configuration de touches
        self.configWindow = ConfigWindow(self)

        # --- HOLD CANVAS --- #
        self.hold_canvas = Canvas(self.master, width= 2 * Config.PIXEL_SIZE, height= 2 * Config.PIXEL_SIZE, bg=Config.COLORS[0], bd=0, highlightthickness=0)
        self.hold_canvas.pack(side='left', padx=10)

        # --- MAIN CANVAS --- #
        self.canvas = Canvas(self.master, width=Config.CANVAS_WIDTH, height=Config.CANVAS_HEIGHT, bg=Config.COLORS[0], bd=0, highlightthickness=0)
        self.canvas.pack(side='left')

        # --- CONFIGURE BINDS --- #
        self.configure_bind = Button(self.master, text="Configurer les touches", command=self.open_bind_window)
        self.configure_bind.pack(pady=5)

        # ------ RESTART BOUTON ------ #
        self.restart_button = Button(self.master, text="Redemarrer la partie", command=self.restart_game)
        self.restart_button.pack()

        # --- LEVEL --- #
        self.level_var = StringVar()
        self.level_label = Label(self.master, textvariable=self.level_var, bg='grey25', foreground='white', width=10)
        self.level_label.pack(pady=(30, 10), padx=30)

        # --- SCORE --- #
        self.score_var = StringVar()
        self.score_label = Label(self.master, textvariable=self.score_var, bg='white', width=10)
        self.score_label.pack(pady=(10, 30), padx=30)

        # --- NEXT TETRI --- #
        self.next_tetri_canv = [Canvas(self.master, width= 2 * Config.PIXEL_SIZE, height= 2 * Config.PIXEL_SIZE, bg=Config.COLORS[0], bd=0, highlightthickness=0) for _ in range(5)]
        for canv in self.next_tetri_canv:
            canv.pack(pady=5, padx=5)

        # --- SOUND --- #
        self.sound()

    def sound(self):
        pygame.init()
        APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))
        full_path = os.path.join(APP_FOLDER, "SON")
        self.music = pygame.mixer.Sound(os.path.join(full_path, "Music.wav"))
        self.bruit = [pygame.mixer.Sound(os.path.join(full_path, "1_lines.wav")), pygame.mixer.Sound(os.path.join(full_path, "2_lines.wav")), pygame.mixer.Sound(os.path.join(full_path, "3_lines.wav")), pygame.mixer.Sound(os.path.join(full_path, "4_lines.wav"))]

    def open_bind_window(self):
        if not self.configWindow.is_open:
            if self.playing:
                self.pause()
            configWindowMaster = Toplevel(self.master)
            self.configWindow.open(configWindowMaster)

    def start_game(self):
        self.playing = True
        self.music.play()
        self.master.bind("<Key>", self.__controls)
        self.master.bind("<KeyRelease>", self.__controls_released)
        self.board = self.__create_board(Config.GRID_WIDTH, Config.GRID_HEIGHT)
        self.message_queue = list()
        self.message_up = False
        self.message_timer = 0
        self.predict = None
        self.next_tetri = [Tetrimino((0, 0), self.next_tetri_canv[i], previsualization=True) for i in range(5)]
        self.change_tetri()
        self.soft_droping = False
        self.spining = False
        self.holded = False
        self.hold_tetri = None
        self.spin_count = 0
        self.tetri_count = 0
        self.speed = Config.SPEED
        self.level = 0
        self.level_var.set("Level : " + str(self.level))
        self.score = 0
        self.score_var.set(str(self.score))
        self.turn = 0
        self.__draw_grid()
        self.update()
        self.master.mainloop()

    def update(self):
        if self.playing:
            self.canvas.tag_raise('message') # On met le message au dessus du reste
            self.canvas.tag_lower('predict') 
            self.canvas.tag_lower('grid') # On met le grid en dessous du reste
            self.turn = self.turn + 1 # Incrémentation du tour actuel
            self.__update_message()
            if not self.current_tetri.move((0,1)):
                if not self.spining:
                    self.spining = True
                    self.spin_count = 1
                else: 
                    if self.spin_count > 0:
                        self.spin_count = self.spin_count - 1
                    elif self.spin_count == 0:
                        self.spining = False
                        if not self.next():
                            self.__stop_game()
                            return
            self.master.after(self.speed, self.update)

    def update_predict(self):
        if self.predict:
            self.canvas.delete('predict')
        self.predict = Tetrimino(self.current_tetri.pos, self.canvas, form=self.current_tetri.form, predict=True, predictParent=self.current_tetri)
        self.predict.go_down()
    
    def next(self):
        if self.holded:
            self.holded = False
        self.tetri_count = self.tetri_count + 1
        if self.tetri_count % 15 == 0:
            self.level = self.level + 1
            self.speed = self.speed - 5
            self.level_var.set("Level : " + str(self.level))
        self.__update_board()
        self.__complete_lines()
        if(self.is_game_over()):
            return False
        self.change_tetri()
        return True

    def change_tetri(self):
        for canv in self.next_tetri_canv:
            canv.delete('all')
        self.current_tetri = Tetrimino((4, -1), self.canvas, form=self.next_tetri[0].form)
        self.update_predict()
        for i in range(len(self.next_tetri) - 1):
            self.next_tetri[i] = Tetrimino((0, 0), self.next_tetri_canv[i], form=self.next_tetri[i + 1].form, previsualization=True)
        self.next_tetri[-1] = Tetrimino((0, 0), self.next_tetri_canv[-1], previsualization=True)

    def is_game_over(self):
        """ Verifie si un tetrimino est au point le plus haut, renvoie True si cest le cas"""
        for box in self.canvas.find_withtag('tetri'):
            _, y, _, _ = self.canvas.coords(box)
            if y < 0:
                return True
        return False

    def pause(self):
        if self.playing:
            pygame.mixer.pause()
            self.playing = not self.playing
            self.paused_message = self.canvas.create_text(0,0, text="PAUSE", anchor='nw', fill='red', tag='pause_message', font=("Helvetica", 26))
            coords = self.canvas.bbox(self.paused_message)
            xOffset = (Config.CANVAS_WIDTH / 2) - (coords[2] - coords[0]) / 2
            yOffset = (Config.CANVAS_HEIGHT / 2) - (coords[3] - coords[1]) / 2
            self.canvas.move(self.paused_message, xOffset, yOffset)
            self.canvas.tag_raise('pause_message')

        else:
            pygame.mixer.unpause()
            self.playing = not self.playing
            self.canvas.delete(self.paused_message)
            self.update()

    def __stop_game(self):
        pygame.mixer.stop()
        self.playing = False
        self.master.unbind("<Key>")
        restart = self.lossmsgbox = askretrycancel("Perdu, gros nullos", "Voulez vous réessayer ?")
        if restart:
            self.restart_game()
        return

    def restart_game(self):
        if not self.playing:
            self.canvas.delete('all')
            self.hold_canvas.delete('all')
            for canv in self.next_tetri_canv:
                canv.delete('all')
            self.start_game()
        else:
            self.__system_message(text="La partie doit être en pause", timer=1000)


    # /!\ A REVOIR /!\ 
    def __update_board(self):
        """ Parcours tout les tetriminos pour etablir une matrice de la grille de jeu avec des 0 et des 1 """
        self.board = self.__create_board(Config.GRID_WIDTH, Config.GRID_HEIGHT)
        for box in self.canvas.find_withtag('tetri'):
            x, y, _,_ = self.canvas.coords(box)
            x = int(x / Config.PIXEL_SIZE)
            y = int(y / Config.PIXEL_SIZE)
            try:
                self.board[y][x] = 1
            except IndexError:
                return False
        return True

    def __create_board(self, width, height):
        return [[0 for _ in range(width)] for _ in range(height)]
    
    def __draw_grid(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.canvas.create_rectangle(j * Config.PIXEL_SIZE, i * Config.PIXEL_SIZE, (j+1) * Config.PIXEL_SIZE, (i+1) * Config.PIXEL_SIZE, outline='gray10', tag='grid')

    def __complete_lines(self):
        """ Verifie chaque ligne du board pour trouver si une est complete, dans ce cas les lignes complete sont suprime"""
        indexes = [i for i, x in enumerate(self.board) if sum(x) == Config.GRID_WIDTH] # Liste des index des lignes complete
        completed_lines = len(indexes) # Le nombre de lignes complete (pour le score)
        for k in indexes:
            self.board[k] = [0 for _ in range(Config.GRID_WIDTH)]
            # Suppresion de toute les cases de la ligne complete
            for box in self.canvas.find_overlapping(0, k * Config.PIXEL_SIZE + 1, Config.GRID_WIDTH * Config.PIXEL_SIZE, (k+1) * Config.PIXEL_SIZE - 1):
                if 'tetri' in self.canvas.gettags(box):
                    self.canvas.delete(box)
            # Descente de une unite pour chaque bloc au dessus de la ligne complete 
            for box in self.canvas.find_overlapping(0, 0, Config.GRID_WIDTH * Config.PIXEL_SIZE, k * Config.PIXEL_SIZE - 1):
                if 'tetri' in self.canvas.gettags(box):
                    self.canvas.move(box, 0, Config.PIXEL_SIZE)
        if completed_lines > 0: # Si une ligne a ete complete on affiche un message et on update le score
            self.__system_message(text=Config.COMPLETE_QUOTES[completed_lines - 1], timer=1500)
            self.__score_calculation(completed_lines)
            self.bruit[completed_lines - 1].play()
        self.__update_board() # Refresh du board pour la suite

    def __score_calculation(self, completed_lines):
        """ Calcul et met a jour le score en prenant en compte le niveau et le nombre de lignes complete"""
        multiplier = [40, 100, 300, 1200]
        # Calcul pour n = le niveau : [multiplieur lie aux nombres de lignes complete] * (n + 1) 
        self.score = self.score + multiplier[completed_lines - 1] * (self.level + 1)
        self.score_var.set(self.score)

    # --- Gestion des evenements claviers --- #
    def hold(self):
        """Permet de sauvegarder le tetrimino actuel pour l'echanger avec celui sauvegarder avant (passe au suivant si il n'y a pas eu de sauvegarde avant)"""
        if not self.holded:
            self.hold_canvas.delete('all')
            self.holded = True
            if not self.hold_tetri:
                self.current_tetri.destroy()
                self.hold_tetri = Tetrimino((0,0), self.hold_canvas, form=self.current_tetri.base_form, previsualization=True)
                self.next()
            else:
                hold_form = self.hold_tetri.form
                pos = self.current_tetri.position
                self.hold_tetri = Tetrimino((0,0), self.hold_canvas, form=self.current_tetri.base_form, previsualization=True)
                self.current_tetri.destroy()
                self.current_tetri = Tetrimino(pos, self.canvas, form=hold_form)

    def __controls(self, event):
        if self.playing:
            if event.keycode == Config.HOTKEYS[0]:
                self.current_tetri.move((-1,0)) # Mouvement gauche
                self.update_predict()
            elif event.keycode == Config.HOTKEYS[1]:
                self.current_tetri.move((1,0)) # Mouvement droit
                self.update_predict()
            elif event.keycode == Config.HOTKEYS[2]:
                self.current_tetri.rotate() # Rotation du tetrimino
                self.update_predict()
            elif event.keycode == Config.HOTKEYS[3]:
                self.current_tetri.go_down() # Hard drop du tetrimino
                self.next()
            elif event.keycode == Config.HOTKEYS[4]:
                if not self.soft_droping:
                    self.soft_droping = True
                    self.speed = int(self.speed / 4)
            elif event.keycode == Config.HOTKEYS[5]:
                self.hold()
                self.update_predict()
        if event.keycode == Config.HOTKEYS[6]:
            self.pause()

    def __controls_released(self, event):
        if event.keycode == Config.HOTKEYS[4]:
            if self.soft_droping:
                self.soft_droping = False
                self.speed = self.speed * 4
    # -------------------------------------------- #

    # ----------------- SYSTEM MESSAGES METHODS ----------------- #
    def __system_message(self, text=None, timer=None, priority=False):
        """ Creer un system message (message affiche milieu haut de lecran), si un autre message est deja affiche le message passe est mis en attente"""
        if not self.message_up:
            if self.message_queue and not text and not timer:
                self.__create_message(self.message_queue[0][0], self.message_queue[0][1])
                del self.message_queue[0]
            elif text and timer:
                self.__create_message(text, timer)
        else:
            if priority:
                self.message_queue.insert(0, (text, timer))
            else:
                self.message_queue.append((text, timer))
        return

    def __create_message(self, text, timer):
        self.message = self.canvas.create_text(0, 0, text=text, anchor='nw', fill=choice(Config.COLORS[1:]), tag='message', font=("Helvetica", 18))
        self.message_up = True
        self.message_timer = int(timer//self.speed)
        coords = self.canvas.bbox(self.message)
        xOffset = (Config.CANVAS_WIDTH / 2) - (coords[2] - coords[0]) / 2
        self.canvas.move(self.message, xOffset, 50)

    def __update_message(self):
        if self.message_up:
            self.message_timer = self.message_timer - 1
            self.message_up = self.message_timer > 0 
            if not self.message_up:
                self.__delete_message()
    
    def __delete_message(self):
        self.canvas.delete(self.message)
        if self.message_queue:
            self.__system_message()
    # ---------------------------------- #


if __name__ == "__main__":
    tetris = Tetris()
    tetris.start_game()
