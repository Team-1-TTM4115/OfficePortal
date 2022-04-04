import time
import tkinter as tk
from tkinter import *

from clock import Clock
from news import News


class Screen:

    def __init__(self):
        self.root = None
        self.startup_screen = tk.Tk()
        self.welcome_text = tk.Label(self.startup_screen, font=('caviar dreams', 40), bg='black', fg='white')
        # Gets the requested values of the height and width.
        self.windowWidth = self.startup_screen.winfo_reqwidth()
        self.windowHeight = self.startup_screen.winfo_reqheight()
        self.frames = {}

    def configure_startup_screen(self) -> None:
        """
        Configures the startup screen. Can be used to display a screen
        while we are waiting to connect/load something.
        :return: None
        """
        self.startup_screen.title('Office Portal')
        self.startup_screen.configure(background='black')
        self.startup_screen.overrideredirect(True)
        self.welcome_text.config(text='Hasta La Pasta')
        self.welcome_text.pack(side=LEFT, padx=120, pady=80)
        # Wrongfully gets both half the screen width/height and window width/height
        positionRight = int(self.startup_screen.winfo_screenwidth() / 2.5 - self.windowWidth / 2)
        positionDown = int(self.startup_screen.winfo_screenheight() / 2 - self.windowHeight / 2)

        # Positions the window in the center of the page and updates the label.
        self.startup_screen.geometry("+{}+{}".format(positionRight, positionDown))
        self.startup_screen.update()
        # Waits two seconds so we are able to se the loading screen.
        time.sleep(2)
        # Removes the startup screen.
        self.startup_screen.destroy()

    def setup_main_screen(self) -> None:
        """
        Sets up the main screen for the magic mirror. Used
        to add the different modules to the root screen.
        :return: None
        """
        # Creates and configures the main screen.
        self.root = tk.Tk()
        self.root.title('Mirror')
        self.root.attributes("-fullscreen", True)
        self.root.configure(background='black')
        self.create_start_page(self.root)
        self.create_test_page(self.root)

    def create_start_page(self, root: tk.Tk):
        start_frame = tk.Frame(root, bg='black')
        start_frame.pack(expand=True, fill="both", side=TOP)
        # Creates the clock object on the main screen.
        clock = Clock(start_frame)
        clock.display_time()
        clock.display_date()
        # Creates the news object on the main screen.
        news_tab = News(start_frame)
        news_tab.show_news()
        button = tk.Button(start_frame, text="Go to next",
                           command=lambda: self.show_frame("test_page"))
        button.pack(side=LEFT)
        self.frames['start_frame'] = start_frame
        start_frame.grid(row=0, column=0, sticky="nsew")

    def create_grid_frame(self, root):
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


    def create_test_page(self, root):
        test_frame = tk.Frame(root, bg='black')
        button = tk.Button(test_frame, text="Go to start",
                           command=lambda: self.show_frame("start_frame"))
        button.pack(side=LEFT)
        self.frames['start_frame'] = test_frame
        self.frames['test_page'] = test_frame
        test_frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_name):
        '''Show a frame for the given page name'''
        frame = self.frames[frame_name]
        frame.tkraise()

    def set_background_img(self):
        # TODO: Emile?
        # Add image file
        bg = PhotoImage(file="Your_img.png")

    def run(self) -> None:
        """
        Runs the program and calls the tkinter mainloop function.
        Nb: Any code written below the mainloop function will not be executed.
        :return: None
        """
        self.configure_startup_screen()
        self.setup_main_screen()
        self.root.mainloop()


if __name__ == "__main__":
    screen = Screen()
    screen.run()
