import time
import tkinter as tk
from tkinter import *


class Clock:
    def __init__(self, screen):
        self.screen = screen
        self.clock_frame = None

        # The scripts to run on creation of the object.
        self.create_clock()

    def create_clock(self) -> None:
        self.clock_frame = tk.Label(self.screen, font=('caviar dreams', 130), bg='black', fg='white')
        self.clock_frame.pack(in_=self.screen, side=TOP)

    def display_time(self) -> None:
        current_time = time.strftime('%H:%M:%S %p')
        self.clock_frame.config(text=current_time)
        self.clock_frame.after(1000, self.display_time)
