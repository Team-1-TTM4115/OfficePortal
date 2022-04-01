import tkinter as tk
from tkinter import *
import time
from newsapi import NewsApiClient
import os


class Screen:

    def __init__(self, startup_text="hello"):
        self.root = None
        self.startup_screen = tk.Tk()
        self.welcome_text = tk.Label(self.startup_screen, font=('caviar dreams', 40), bg='black', fg='white')
        # Gets the requested values of the height and widht.
        self.windowWidth = self.startup_screen.winfo_reqwidth()
        self.windowHeight = self.startup_screen.winfo_reqheight()
        self.clock = None
        # TODO: move all below to another class
        self.decrypt = list()
        self.iteration = 0
        self.timecount = 0
        self.repull = 0
        self.sleep = 0
        self.api = NewsApiClient(api_key='015d990f2921480d8de32074f9d4f64a')
        self.newstitle = None
        self.source = None

    def configure_startup_screen(self):
        self.startup_screen.title('Magic Mirror: Python Mod')
        self.startup_screen.configure(background='black')
        self.startup_screen.overrideredirect(True)
        self.welcome_text.config(text='Hasta La Pasta')
        self.welcome_text.pack(side=LEFT, padx=120, pady=80)
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.startup_screen.winfo_screenwidth() / 3 - self.windowWidth / 2)
        positionDown = int(self.startup_screen.winfo_screenheight() / 2 - self.windowHeight / 2)

        # Positions the window in the center of the page.
        self.startup_screen.geometry("+{}+{}".format(positionRight, positionDown))
        self.startup_screen.update()
        time.sleep(2)  # Waits two seconds so we are able to se the loading screen.
        self.startup_screen.destroy()

    def setup_main_screen(self):
        self.root = tk.Tk()
        self.root.title('Mirror')
        self.clock = Clock(self.root)
        self.newstitle = tk.Label(self.root, font=('caviar dreams', 30), bg='black', fg='white')
        self.newstitle.pack(side=BOTTOM, anchor=W, fill=X)
        self.source = tk.Label(self.root, font=('caviar dreams', 20), bg='black', fg='white')
        self.source.pack(side=BOTTOM, anchor=W, fill=X)
        self.root.attributes("-fullscreen", True)
        self.root.configure(background='black')

    def news_header(self, ):
        """
        This function iterates over the news headlines. Iteration is the news number,
        'itemlist' brings out only the title.
        """
        itemlist = self.decrypt[self.iteration]
        self.newstitle.config(text=itemlist['title'])
        self.source.config(text=itemlist['author'])
        if self.iteration < 9:
            self.iteration += 1
        else:
            iteration = 0

    def run(self):
        running = True
        self.configure_startup_screen()
        self.setup_main_screen()
        self.headlines = self.api.get_top_headlines(sources='bbc-news')
        # print(headlines)
        payload = self.headlines
        self.decrypt = (payload['articles'])
        maxrange = len(self.decrypt)

        while running:
            self.news_header()
            self.clock.time()
            # TODO: Figure out if we should use mainloop or not.
            self.root.mainloop()


class Clock:
    def __init__(self, screen):
        self.screen = screen
        self.decrypt = list()
        self.iteration = 0
        self.timecount = 0
        self.repull = 0
        self.sleep = 0
        self.api = NewsApiClient(api_key='015d990f2921480d8de32074f9d4f64a')
        self.clock_frame = None
        self.clock_frame2 = None
        self.newstitle = None
        self.source = None
        self.master_clock = None

        # The scripts to run on creation
        self.create_clock()

    def create_clock(self):
        self.master_clock = tk.Label(self.screen)
        self.master_clock.pack(anchor=NW, fill=X, padx=45)
        self.master_clock.configure(background='black')
        self.clock_frame = tk.Label(self.screen, font=('caviar dreams', 130), bg='black', fg='white')
        self.clock_frame.pack(in_=self.master_clock, side=LEFT)
        self.clock_frame2 = tk.Label(self.screen, font=('caviar dreams', 70), bg='black', fg='white')
        self.clock_frame2.pack(in_=self.master_clock, side=LEFT, anchor=N, ipady=15)

    def time(self):
        current_time = time.strftime('%H:%M:%S %p')
        self.clock_frame.config(text=current_time)
        self.clock_frame.after(1000, self.time)

    def tick(self, time1=''):
        time2 = time.strftime("%H")
        if time2 != time1:
            time1 = time2
            self.clock_frame.config(text=time2)
        self.clock_frame.after(200, self.tick)

    def tickk(self, time3=''):
        time4 = time.strftime(":%M:%S")
        if time4 != time3:
            time3 = time4
            self.clock_frame2.config(text=time4)
        self.clock_frame2.after(200, self.tickk)

    # This function waits for a certain amount of 'tocks' and then initiates 'newsheader' -function
    def tock(self):
        if self.timecount < 20:
            self.timecount += 1
        else:
            self.timecount = 0
        if self.repull < 200:
            self.repull += 1
        else:
            self.repull = 0
        if self.sleep < 800:
            self.sleep += 1
        else:
            sleep = 0
            # motiondetector()


class News:
    pass


if __name__ == "__main__":
    screen = Screen()
    screen.run()
