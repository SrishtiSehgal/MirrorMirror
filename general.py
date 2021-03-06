# import modules
from tkinter import *  
import requests, json, traceback, datetime, pytz
from PIL import Image, ImageTk
from components.weather import WeatherFunc
from components.clock import Clock

class FullscreenWindow:
    """ Creates application/interface for smart mirror"""
    def __init__(self)->None:
        self.tk = Tk()
        self.tk.configure(background='black')
        # self.topFrame = Frame(self.tk, background = 'black')
        # self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        # self.bottomFrame = Frame(self.tk, background = 'black')
        # self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

        # weather
        self.weather = WeatherFunc(self.tk)
        self.weather.ask_weather()

        # clock
        self.clock = Clock(self.tk, self.weather.weather_data['current']['dt'])
        
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