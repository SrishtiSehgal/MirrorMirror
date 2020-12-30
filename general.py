# import modules
from tkinter import *  
import requests, json, traceback, datetime, pytz
from PIL import Image, ImageTk
from components.weather import WeatherFunc

class FullscreenWindow:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        # self.bottomFrame = Frame(self.tk, background = 'black')
        # self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        # clock
        # self.clock = Clock(self.topFrame)
        # self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
        
        # weather
        self.weather = WeatherFunc(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
        self.weather.ask_weather()
        
        # news
        # self.news = News(self.bottomFrame)
        # self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)
        # calender - removing for now
        # self.calender = Calendar(self.bottomFrame)
        # self.calender.pack(side = RIGHT, anchor=S, padx=100, pady=60)
        
        # buttons
        self.on = False

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()