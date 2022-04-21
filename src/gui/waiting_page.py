import tkinter as tk
from tkinter import CENTER


class WaitingPage:

    def __init__(self, parent_frame, width, height):
        self.waiting_frame = None
        self.count = 1
        self.parent_frame = parent_frame
        self.width = width
        self.height = height
        self.waiting_text = "Waiting to connect"
        self.dots = "."
        self.waiting_label = None

    def create_waiting_page(self):
        """
        Creates the waiting page.
        :return: None
        """
        waiting_frame = tk.Frame(self.parent_frame, bg='black')
        self.waiting_frame = waiting_frame
        waiting_frame.grid(row=0, column=0, sticky="nsew", )
        self.waiting_label = tk.Label(self.waiting_frame, text=self.waiting_text, bg='black', fg='white',
                                      font=("Helvetica", 40))
        self.waiting_label.place(x=self.width / 2, y=self.height / 2, anchor=CENTER)
        self.update_waiting_page()
        return waiting_frame

    def update_waiting_page(self):
        """
        Updates the waiting page.
        :return: None
        """
        dots = ""
        waiting_text = 'Waiting to connect'
        if self.count > 3:
            self.count = 1
        for _ in range(self.count):
            dots += "."
        self.waiting_text = waiting_text + dots
        self.waiting_label.config(text=self.waiting_text)
        self.count += 1
        self.waiting_frame.after(1000, self.update_waiting_page)
