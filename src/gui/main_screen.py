import time
import tkinter as tk
from tkinter import *

import cv2
from PIL import Image, ImageTk
from src.gui.clock import Clock
from src.gui.news import News
from qr.qr_scanner import QrReader


class Screen:

    def __init__(self):
        # Gets the requested values of the height and width.
        self.root = tk.Tk()
        self.root.withdraw()
        self.frames = {}
        self.frame_container = None
        self.height = None
        self.width = None
        self.qr_reader = None

    def configure_startup_screen(self) -> None:
        """
        Configures the startup screen. Can be used to display a screen
        while we are waiting to connect/load something.
        :return: None
        """
        # The startup-screen.
        # tk.NoDefaultRoot()  # may be redundant or may help clean up memory.
        startup_screen = tk.Tk()
        startup_screen.overrideredirect(True)
        startup_screen.wm_attributes("-transparent", True)
        startup_screen.title('Office Portal')
        startup_screen.configure(background='black')
        # startup_screen.overrideredirect(True)
        # The welcome text
        welcome_text = tk.Label(startup_screen, font=('caviar dreams', 40), bg='black', fg='white')
        welcome_text.config(text='Hasta La Pasta')
        welcome_text.pack(side=LEFT, padx=120, pady=80)
        # Fetches the window size.
        window_width = startup_screen.winfo_reqwidth()
        window_height = startup_screen.winfo_reqheight()
        # Wrongfully gets both half the screen width/height and window width/height
        position_right = int(startup_screen.winfo_screenwidth() / 2.5 - window_width / 2)
        position_down = int(startup_screen.winfo_screenheight() / 2 - window_height / 2)

        # Positions the window in the center of the page and updates the label.
        startup_screen.geometry("+{}+{}".format(position_right, position_down))
        startup_screen.update()
        # Waits two seconds for the loading screen.
        time.sleep(2)
        # Removes the startup screen.
        welcome_text.destroy()
        startup_screen.destroy()

    def create_main_screen(self) -> tk.Tk:
        """
        Sets up the main screen for the magic mirror. Used
        to add the different modules to the root screen.
        :return: None
        """
        # Creates and configures the main screen.
        root = self.root
        root.deiconify()
        root.title('Office Portal')
        root.attributes("-fullscreen", True)
        root.configure(background='black')
        self.height = root.winfo_screenheight()
        self.width = root.winfo_screenwidth()
        frame_container = self.create_grid_frame(root)
        self.frame_container = frame_container
        # TODO: Remove from here. GUI controller should be responsible for this.
        self.create_start_page(frame_container)
        self.create_video_page(frame_container)
        self.create_qr_page()
        self.create_filter_page(frame_container)
        self.show_frame("start_frame")
        return root

    def create_start_page(self, parent_frame: tk.Frame) -> None:
        """
        Creates and adds the different modules to the start page.
        :param parent_frame The parent frame
        :return: None
        """
        start_frame = tk.Frame(parent_frame, bg='black')
        start_frame.pack(expand=False, fill=BOTH, side=TOP, anchor=CENTER)
        # Creates the clock object on the main screen.
        clock = Clock(start_frame)
        clock.display_time()
        clock.display_date()
        # Creates the news object on the main screen.
        news_tab = News(start_frame)
        news_tab.show_news()
        button = tk.Button(start_frame, text="Go to next",
                           command=lambda: self.show_frame("video_frame"))
        button.place(anchor=CENTER, relx=0.5, rely=0.5)
        self.frames['start_frame'] = start_frame
        start_frame.grid(row=0, column=0, sticky="nsew")

    def create_grid_frame(self, root) -> tk.Frame:
        """
        Creates the grid that keeps the frames.
        :param root: The root window
        :return: None
        """
        frame_container = tk.Frame(root, bg='white')
        frame_container.pack(fill="both", expand=True)
        frame_container.grid_rowconfigure(0, weight=1)
        frame_container.grid_columnconfigure(0, weight=1)
        return frame_container

    def create_video_page(self, root):
        test_frame = tk.Frame(root, bg='black')
        label = tk.Label(test_frame, text="Video page", bg='black', fg='white')
        button1 = tk.Button(test_frame, text="Go to picture frame",
                            command=lambda: self.show_frame("start_frame"))
        button2 = tk.Button(test_frame, text="Go to filter page",
                            command=lambda: self.show_frame("filter_frame"))
        button3 = tk.Button(test_frame, text="Go to qr page",
                            command=lambda: self.show_frame("qr_frame"))
        label.pack(side=TOP, fill=X)
        button1.pack(anchor=CENTER)
        button2.pack(anchor=CENTER)
        button3.pack(anchor=CENTER)
        self.frames['video_frame'] = test_frame
        test_frame.grid(row=0, column=0, sticky="nsew", )

    def create_filter_page(self, root):
        filter_frame = tk.Frame(root, bg='black')
        label = tk.Label(filter_frame, text="Filter page", bg='black', fg='white')
        button1 = tk.Button(filter_frame, text="Go to video frame",
                            command=lambda: self.show_frame("video_frame"))

        label.pack(anchor=N)
        button1.pack(anchor=CENTER)
        self.frames['filter_frame'] = filter_frame
        filter_frame.grid(row=0, column=0, sticky="nsew", )

    def create_qr_page(self):
        if self.frame_container:
            qr_frame = tk.Frame(self.frame_container, bg='black')
            print(self.width, self.height)
            self.frames['qr_frame'] = qr_frame
            qr_frame.grid(row=0, column=0, sticky="nsew")
            self.qr_reader = QrReader(qr_frame, self.width, self.height)
            self.qr_reader.capture_video()
        else:
            Exception("Frame container is not defined")

    def destroy_qr_page(self):
        self.qr_reader.destroy_video()

    def show_frame(self, frame_name) -> None:
        """
        Show a frame for the given page name
        :param frame_name: The name you want to show.
        :return: None
        """
        frame = self.frames[frame_name]
        print(frame)
        frame.tkraise()

    def set_background_img(self):
        # TODO: Emile?
        # Add image file
        bg = PhotoImage(file="Your_img.png")

    def run(self) -> None:
        """
        Runs the program and calls the tkinter mainloop function.
        Nb: Any code written below the mainloop function will not be
        executed.
        :return: None
        """
        self.configure_startup_screen()
        root = self.create_main_screen()
        root.mainloop()
