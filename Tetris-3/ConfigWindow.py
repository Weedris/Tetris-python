from tkinter import Tk, Label, Button, StringVar, Scale
from tkinter.messagebox import askquestion
from Config import Config


class ConfigWindow:
    def __init__(self, parent=None, debug=False):
        self.parent = parent
        self.opened = False
        self.debug = debug

    def open(self, master):
        self.master = master
        self.master.configure(background='grey25')
        self.opened = True
        self.master.title("Configurations")
        self.master.protocol("WM_DELETE_WINDOW", self.dispose)
        self.create_widgets()
        self.master.mainloop()
    
    def create_widgets(self):
        self.touches_titre = Label(self.master, text="Touches :", justify="center", background='grey25', fg='white')
        self.touches_titre.grid(column=0, row=0, columnspan=3, pady=5)
        self.binding = False
        self.bindbuttons = [BindButton(self, self.master, i, column= i % 3, row=int(i / 3) + 1) for i in range(len(Config.HOTKEYS) - 1)]
        self.difficulte_titre = Label(self.master, text="Difficulté :", justify="center", background='grey25', fg='white')
        self.difficulte_titre.grid(column=0, row=4, columnspan=3, pady=5)
        self.difficulte_scale = Scale(self.master, orient='horizontal', background='grey25', showvalue=0, fg='white', from_=0, to=len(Config.BASE_DIFFICULTIES) - 1, resolution=1, tickinterval=1, length=300, command=self.difficulte_change)
        self.difficulte_scale.set(Config.DIFFICULTE)
        self.difficulte_scale.grid(column=0, row=5, columnspan=3, padx=5)
        if self.debug:
            self.debug_titre = Label(self.master, text="Debug :", justify="center", background='grey25', fg='white')
            self.debug_titre.grid(column=0, row=6, columnspan=3, pady=5)
            self.load_button = Button(self.master, text="Charger", command=lambda: Config.load())
            self.load_button.grid(column=0, row=7, pady=5)
            self.save_button = Button(self.master, text="Sauvegarder", command=lambda : Config.save())
            self.save_button.grid(column=1, row=7, pady=5)
            self.show_config_button = Button(self.master, text="Afficher", command=lambda : print(Config.toString()))
            self.show_config_button.grid(column=2, row=7, pady=5)

    def dispose(self):
        self.opened = False
        save = askquestion("Fermeture", "Voulez vous sauvegarder les changements ?")
        if save == 'yes':
            Config.save()
        Config.load()
        if self.parent:
            self.parent.pause()
        self.master.destroy()

    def reload(self):
        for widgets in self.master.grid_slaves():
            widgets.grid_forget()
        self.create_widgets()

    def difficulte_change(self, value):
        Config.DIFFICULTE = int(value)
        Config.SPEED = Config.BASE_DIFFICULTIES[Config.DIFFICULTE]

    def enable_debug(self, value: bool):
        print(value)
        self.debug = value
        self.reload()

    @property
    def is_open(self):
        return self.opened


class BindButton:
    def __init__(self, parent, master, index: int, column=0, row=0):
        self.index = index
        self.master = master
        self.keyPressed = False
        self.button_text = StringVar()
        self.parent = parent
        self.button_text.set(Config.HOTKEYS_LABEL[self.index] + ": " + str(Config.HOTKEYS[self.index]))
        self.button = Button(self.master, textvariable=self.button_text, command=self.start_binding, bg='ivory', relief='flat', width=10)
        self.button.grid(column=column, row=row, pady=5, padx=5)

    def start_binding(self):
        if not self.parent.binding:
            self.button.configure(bg='lightpink1')
            self.parent.binding = True
            self.binding()
        return

    def binding(self):
        self.master.bind("<Key>", self.keyListener)
        if self.keyPressed:
            self.button.configure(bg='ivory', relief='flat')
            self.master.unbind("<Key>")
            Config.HOTKEYS[self.index] = self.keyCode
            self.button_text.set(Config.HOTKEYS_LABEL[self.index] + ": " + str(Config.HOTKEYS[self.index]))
            self.keyPressed = False
            self.parent.binding = False
            return
        elif self.keyPressed:
            return
        self.master.after(10, self.binding)

    def keyListener(self, event):
        self.keyPressed = True
        self.keyCode = event.keycode

    @property
    def get_index(self):
        return self.index


if __name__ == "__main__":
    master = Tk()
    configWindow = ConfigWindow(debug=True)
    configWindow.open(master)
