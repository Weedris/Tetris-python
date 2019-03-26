from random import choice
from Config import Config


class Tetrimino:
    def __init__(self, startpos, canvas, form=None, previsualization=False, predict=False, predictParent=None):
        if not form:
            self.__form = choice(Config.TETRI_LIST)
        else:
            self.__form = form
        self.__base_form = self.__form
        self.predict_parent = predictParent
        self.__canvas = canvas
        self.predict = predict
        x, y = startpos
        if previsualization:
            self.__pixel_size = Config.PIXEL_SIZE * 0.5
            y = (int(self.__canvas['height']) / self.__pixel_size) / 2 - max(self.__form, key=lambda x: x[1])[1]
            x = (int(self.__canvas['width']) / self.__pixel_size) / 2 - max(self.__form, key=lambda x: x[0])[0]
        else:
            self.__pixel_size = Config.PIXEL_SIZE
            y = 0 - max(self.__form, key=lambda x: x[0])[0]
            if x + max(self.__form, key=lambda x: x[0])[0] + 1 > Config.GRID_WIDTH - 1:
                x =  Config.GRID_WIDTH - (max(self.__form, key=lambda x: x[0])[0] + 1)
        self.pos = (x, y)
        self.boxes = self.__create(self.pos)

    def rotate(self):
        new_pos = self.__after_rotate_pos()
        must_movex = list()
        for i, box in enumerate(self.boxes):
            if self.__canvas.coords(box)[2] / self.__pixel_size + new_pos[i][0] > Config.GRID_WIDTH:
                must_movex.append((self.__canvas.coords(box)[2] / self.__pixel_size + new_pos[i][0]) - Config.GRID_WIDTH)
            else:
                must_movex.append(0)
        self.move((-max(must_movex), 0))
        if not all(self.__can_move(self.__canvas.coords(box), new_pos[i]) for i, box in enumerate(self.boxes)):
            self.move((0, -1))

        if all(self.__can_move(self.__canvas.coords(box), new_pos[i]) for i, box in enumerate(self.boxes)):
            self.__form = self.__rotate()
            for i, box in enumerate(self.boxes):
                x, y = new_pos[i]
                self.__canvas.move(box, x * self.__pixel_size, y * self.__pixel_size)

    def move(self, direction):
        if all(self.__can_move(self.__canvas.coords(box), direction) for box in self.boxes):
            move_x, move_y = direction
            self.pos = (self.pos[0] + move_x, self.pos[1] + move_y)
            for box in self.boxes:
                self.__canvas.move(box, self.__pixel_size * move_x, self.__pixel_size * move_y)
            return True
        return False

    def go_down(self):
        y_translate = 1
        while all(self.__can_move(self.__canvas.coords(box), (0, y_translate)) for box in self.boxes):
            y_translate += 1
        self.move((0, y_translate - 1))

    def destroy(self):
        for box in self.boxes:
            self.__canvas.delete(box)

    # ---------------- PRIVATE ---------------- #

    def __after_rotate_pos(self):
        rotate = self.__rotate()
        return [(rotate[k][0] - self.__form[k][0],
                rotate[k][1] - self.__form[k][1]) for k in range(len(self.__form))]

    def __rotate(self):
        """ Renvoie les coordonees du tetrimino apres rotation"""
        max_x = max(self.__form, key=lambda x: x[0])[0]

        rotated = [(max_x - coord[1], \
                    coord[0]) for coord in self.__form]
        min_x = min(rotated, key= lambda x: x[0])[0]
        min_y = min(rotated, key= lambda x: x[1])[1]
        return [(coord[0] - min_x, coord[1] - min_y) for coord in rotated]

    def __can_move(self, coords, translate_pos):
        x, y = translate_pos
        x_left, y_up, x_right, y_bottom = coords
        overlap = set(self.__canvas.find_overlapping(x_left + x * self.__pixel_size + 1, y_up + y * self.__pixel_size + 1, x_right + x * self.__pixel_size - 1, y_bottom + y * self.__pixel_size - 1))
        if self.predict_parent:
            tetris = set(self.__canvas.find_withtag('tetri')) - set(self.boxes) - set(self.predict_parent.boxes)
        else: 
            tetris = set(self.__canvas.find_withtag('tetri')) - set(self.boxes)
        
        can_move = not (y_bottom / self.__pixel_size + y > Config.GRID_HEIGHT or x_left / self.__pixel_size + x < 0 or x_right / self.__pixel_size + x > Config.GRID_WIDTH or overlap & tetris)
        return can_move

    def __create(self, startpos):
        """ Creer tout les carres du tetrimino en fonction de la forme, ils sont equipe du tag 'tetri' """
        col, alt = startpos
        if self.predict:
            color = 'grey16'
            tag = 'predict'
        else: 
            color = self.color
            tag = 'tetri'
        return [self.__canvas.create_rectangle((coord[0] + col) * self.__pixel_size, 
                                            (coord[1] + alt) * self.__pixel_size,
                                            (coord[0] + col + 1) * self.__pixel_size, 
                                            (coord[1] + alt + 1) * self.__pixel_size,
                                            fill=color,
                                            tags=tag) for coord in self.__form]
    # ---------------- PROPERTIES ---------------- #

    @property
    def position(self):
        return self.pos

    @property
    def array(self):
        return [[1 if (j,i) in self.__form else 0 \
                for j in range(max(self.__form, key=lambda x: x[0])[0] + 1)] \
                for i in range(max(self.__form, key= lambda x: x[1])[1] + 1)]

    @property
    def form(self):
        return self.__form

    @property
    def base_form(self):
        return self.__base_form

    @property
    def color(self):
        return Config.COLORS[Config.TETRI_LIST.index(self.__base_form) + 1]

    # ---------------- DEBUG TOOLS ---------------- #

    @property
    def box_coords(self):
        return [self.__canvas.coords(box) for box in self.boxes]
