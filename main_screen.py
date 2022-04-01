import tkinter as tk
from tkinter import *
import time
from newsapi import NewsApiClient
import os


class Screen:

    def __init__(self, startup_text="hello"):
        self.startup_screen = tk.Tk()
        self.welcome_text = tk.Label(self.startup_screen, font=('caviar dreams', 40), bg='black', fg='white')
        # Gets the requested values of the height and widht.
        self.windowWidth = self.startup_screen.winfo_reqwidth()
        self.windowHeight = self.startup_screen.winfo_reqheight()
        # TODO: move all below to another class
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

    def configure_startup_screen(self):
        self.startup_screen.title('Magic Mirror: Python Mod')
        self.startup_screen.configure(background='black')
        self.startup_screen.overrideredirect(True)
        self.welcome_text.config(text='Mirror: Vuoristo Mod')
        self.welcome_text.pack(side=LEFT, padx=120, pady=80)
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.startup_screen.winfo_screenwidth() / 3 - self.windowWidth / 2)
        positionDown = int(self.startup_screen.winfo_screenheight() / 2 - self.windowHeight / 2)

        # Positions the window in the center of the page.
        self.startup_screen.geometry("+{}+{}".format(positionRight, positionDown))
        self.startup_screen.update()

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
        self.newstitle.after(200, self.tock)
        if self.timecount < 20:
            self.timecount += 1
        else:
            self.timecount = 0
            self.news_header()
        if self.repull < 200:
            self.repull += 1
        else:
            self.repull = 0
            headlines = self.api.get_top_headlines(sources='bbc-news')
            payload = headlines
            decrypt = (payload['articles'])
            maxrange = len(decrypt)
        if self.sleep < 800:
            self.sleep += 1
        else:
            sleep = 0
            # motiondetector()

    def news_header(self, ):
        """T
        his function iterates over the news headlines. Iteration is the news number,
        'itemlist' brings out only the title.
        """
        itemlist = self.decrypt[self.iteration]
        # print(itemlist['title'])
        self.newstitle.config(text=itemlist['title'])
        self.source.config(text=itemlist['author'])
        if self.iteration < 9:
            self.iteration += 1
        else:
            iteration = 0

    def run(self):
        running = True
        self.configure_startup_screen()
        while running:
            self.headlines = self.api.get_top_headlines(sources='bbc-news')
            # print(headlines)
            payload = self.headlines
            self.decrypt = (payload['articles'])
            maxrange = len(self.decrypt)

            root = tk.Tk()
            root.title('Mirror')

            masterclock = tk.Label(root)
            masterclock.pack(anchor=NW, fill=X, padx=45)
            masterclock.configure(background='black')
            self.clock_frame = tk.Label(root, font=('caviar dreams', 130), bg='black', fg='white')
            self.clock_frame.pack(in_=masterclock, side=LEFT)
            self.clock_frame2 = tk.Label(root, font=('caviar dreams', 70), bg='black', fg='white')
            self.clock_frame2.pack(in_=masterclock, side=LEFT, anchor=N, ipady=15)
            self.newstitle = tk.Label(root, font=('caviar dreams', 30), bg='black', fg='white')
            self.newstitle.pack(side=BOTTOM, anchor=W, fill=X)
            self.source = tk.Label(root, font=('caviar dreams', 20), bg='black', fg='white')
            self.source.pack(side=BOTTOM, anchor=W, fill=X)

            self.news_header()
            self.tick()
            self.tickk()
            self.tock()

            root.attributes("-fullscreen", True)
            root.configure(background='black')
            self.startup_screen.destroy()
            root.mainloop()


if __name__ == "__main__":
    screen = Screen()
    screen.run()
