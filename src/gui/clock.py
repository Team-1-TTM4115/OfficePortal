import time
import tkinter as tk
from tkinter import *
import datetime as dt


class Clock:
    def __init__(self, screen):
        self.screen = screen
        self.clock_space = None
        self.clock_frame = None
        self.date_frame = None

        # The scripts to run on creation of the object.
        self.create_clock_space()
        self.create_clock()

    def create_clock_space(self) -> None:
        """
        Creates the space dedicated to the clock-module.
        :return: None
        """
        self.clock_space = tk.Label(self.screen)
        self.clock_space.pack(anchor=N, padx=45, pady=50)
        self.clock_space.configure(background='black')

    def create_clock(self) -> None:
        """
        Creates the clock and date frame.
        :return: None
        """
        # Creates the date frame
        self.date_frame = Label(self.clock_space, font=('caviar dreams', 20), bg='black', fg='white')
        self.date_frame.pack(in_=self.clock_space, anchor=N)
        # Creates the time frame
        self.clock_frame = tk.Label(self.clock_space, font=('caviar dreams', 70), bg='black', fg='white')
        self.clock_frame.pack(in_=self.clock_space, anchor=S)

    def display_time(self) -> None:
        """
        Displays the current time. This function is called
        every second to update the current time.
        :return: None
        """
        current_time = time.strftime('%H:%M:%S %p')
        self.clock_frame.config(text=current_time)
        self.clock_frame.after(1000, self.display_time)

    def display_date(self) -> None:
        """
        Displays the current date. This function is called
        every second to update the current time.
        :return: None
        """
        # TODO: maybe not necessary to check each second if its a new date?
        date = dt.datetime.now()
        self.date_frame.config(text=f"{date:%A, %B %d, %Y}")
        self.date_frame.after(1000, self.display_date)
