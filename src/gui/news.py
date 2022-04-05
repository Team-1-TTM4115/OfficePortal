import tkinter as tk
from tkinter import *
import time
from newsapi import NewsApiClient


class News:
    def __init__(self, screen):
        self.screen = screen
        self.api = NewsApiClient(api_key='015d990f2921480d8de32074f9d4f64a')
        self.head_lines = self.api.get_top_headlines(sources='bbc-news')
        self.news_title = None
        self.source = None
        self.iteration = 0

        # The scripts to run on creation of the object.
        self.create_news_tab()
        self.fetch_news()

    def create_news_tab(self) -> None:
        """
        Creates the two different labels used in the news tab.
        The title label is the news headline.
        The source label is the source or "subject" of the news.
        :return:None
        """
        self.news_title = tk.Label(self.screen, font=('caviar dreams', 30), bg='black', fg='white')
        self.news_title.pack(side=BOTTOM, anchor=W, fill=X)
        self.source = tk.Label(self.screen, font=('caviar dreams', 20), bg='black', fg='white')
        self.source.pack(side=BOTTOM, anchor=CENTER, fill=X)

    def fetch_news(self) -> None:
        """
        Fetches the 9 latest news articles from BBC-news.
        :return: None
        """
        self.head_lines = self.api.get_top_headlines(sources='bbc-news')

    def show_news(self) -> None:
        """
        Iterates through the different news articles and displays a new one every third second.
        :return None
        """
        article = self.head_lines['articles'][self.iteration]
        item_list = article
        self.news_title.config(text=item_list['title'])
        self.source.config(text=item_list['author'])
        if self.iteration < 9:
            self.iteration += 1
        else:
            self.iteration = 0
        self.news_title.after(5500, self.show_news)
