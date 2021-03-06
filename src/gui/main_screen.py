import time
import tkinter as tk
from tkinter import *

from PIL import Image, ImageTk

from connection_and_streaming.stream_reciver import StreamVideoReciver
from gui.waiting_page import WaitingPage
from qr.qr_scanner import QrReader
from gui.clock import Clock
from gui.news import News


class Screen:

    def __init__(self, cap, name):
        # Gets the requested values of the height and width.
        self.root = tk.Tk()
        self.root.withdraw()
        self.frames = {}
        self.frame_container = None
        self.height = None
        self.width = None
        self.qr_reader = None
        self.waiting_nr = 1
        self.img_path = r"../img/gallery_img.jpg"
        self.abs_path = r"C:\repos\OfficePortal\src\img\gallery_img.jpg"
        self.stream_video_reciver = None
        self.cap = cap
        self.officeName = name

    def configure_startup_screen(self) -> None:
        """
        Configures the startup screen. Can be used to display a screen
        while we are waiting to connect/load something.
        :return: None
        """
        # The startup-screen.
        startup_screen = tk.Tk()
        startup_screen.overrideredirect(True)
        startup_screen.title('Office Portal')
        startup_screen.configure(background='black')

        # The welcome text
        welcome_text = tk.Label(startup_screen, font=('caviar dreams', 40), bg='black', fg='white')
        welcome_text.config(text='Hasta La Pasta')
        welcome_text.pack(side=LEFT, padx=120, pady=80)

        # Fetches the window size.
        window_width = startup_screen.winfo_reqwidth()
        window_height = startup_screen.winfo_reqheight()
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
        self.create_gallery_page()
        self.stream_video_reciver = StreamVideoReciver(self.officeName)
        self.show_frame("gallery_frame")
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
        button = tk.Button(start_frame, text="Go to filter",
                           command=lambda: self.show_frame("filter_frame"))
        button.pack(anchor=CENTER)
        button2 = tk.Button(start_frame, text="Go to qr",
                            command=lambda: self.show_frame("qr_frame"))
        button2.pack(anchor=CENTER)
        button3 = tk.Button(start_frame, text="Go to waiting",
                            command=lambda: self.show_frame("waiting_frame"))
        button3.pack(anchor=CENTER)

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

    def create_video_page(self):
        """
        Temp video frame.
        :return:
        """
        video_frame = tk.Frame(self.frame_container, bg='black')
        self.frames['video_frame'] = video_frame
        video_frame.grid(row=0, column=0, sticky="nsew", )

        canvas = Canvas(video_frame, bg='black', borderwidth=0)
        canvas.pack(fill=BOTH, expand=YES)
        self.stream_video_reciver.set_canvas(canvas=canvas, height=self.height, width=self.width, gui_frame=video_frame)

    def show_filter(self):
        self.stream_video_reciver.set_is_showing(True)

    def hide_filter(self):
        self.stream_video_reciver.set_is_showing(False)

    def create_gallery_page(self):
        gallery_frame = tk.Frame(self.frame_container, bg='black')
        self.frames['gallery_frame'] = gallery_frame
        gallery_frame.grid(row=0, column=0, sticky="nsew", )

        canvas = Canvas(gallery_frame, width=self.width, height=self.height)
        canvas.pack(fill=BOTH, expand=YES)
        button = tk.Button(gallery_frame, text="Go to filter", )
        button.pack(anchor=CENTER)
        load = Image.open(self.abs_path)
        rezized = load.resize((self.width, self.height), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(rezized)
        self.frame_container.image = image  # to prevent the image garbage collected.
        canvas.create_image((0, 0), image=image, anchor=NW)

    def create_waiting_page(self):
        waiting = WaitingPage(self.frame_container, height=self.height, width=self.width)
        waiting_frame = waiting.create_waiting_page()
        self.frames['waiting_frame'] = waiting_frame

    def destroy_waiting_page(self):
        """
        Destroys the waiting page.
        :return: None
        """
        self.frames['waiting_frame'].destroy()

    def create_qr_page(self):
        """
        Creates the qr page and starts the capture of the video.
        :return: None
        """
        if self.frame_container:
            qr_frame = tk.Frame(self.frame_container, bg='black')
            self.frames['qr_frame'] = qr_frame
            qr_frame.grid(row=0, column=0, sticky="nsew")
            self.qr_reader = QrReader(qr_frame, self.width, self.height, self.officeName, self.cap)

            self.qr_reader.capture_video()
        else:
            Exception("Frame container is not defined")

    def destroy_qr_page(self):
        """
        Destroys the qr page and releases the camera.
        :return:
        """
        self.qr_reader.destroy_video()
        qr_frame: tk.Frame = self.frames['qr_frame']
        qr_frame.destroy()

    def show_frame(self, frame_name) -> None:
        """
        Show a frame for the given page name
        :param frame_name: The name you want to show.
        :return: None
        """
        frame = self.frames[frame_name]
        frame.tkraise()

    def set_background_img(self):
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
