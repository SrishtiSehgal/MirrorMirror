# import modules
from tkinter import *  
import locale
import threading
import time
import requests
import json
import traceback
# import feedparser
import datetime
from PIL import Image, ImageTk
from contextlib import contextmanager

# class WeatherFunc(Frame):
class WeatherFunc:
    DEGREE_SYMBOL = u'\N{DEGREE SIGN}'

    # def __init__(self, parent, *args, **kwargs):
        # Frame.__init__(self, parent, bg='black')
    def __init__(self):
        self.location = '' # dict
        self.apikey = ''
        self.units = ''

        self.current = {
            'curr_temp' : '',
            'curr_sunrise' : '',
            'curr_sunset' : '',
            'curr_feelslike' : '',
            'curr_humidity' : '',
            'curr_uv' : '',
            'curr_visibility' : '',
            'curr_windspeed' : '',
            'curr_windgust' : '',
            'curr_weather' : ''
        }

        self.forecast = {
            'forecast7_temp' : '',
            'forecast7_feelslike' : '',
            'forecast7_weather' : ''
        }

        self.alerts = {
            'alerts_event' : '',
            'alerts_start' : '',
            'alerts_end' : ''
        }
            
        # self.degreeFrm = Frame(self, bg="black")
        # self.degreeFrm.pack(side=TOP, anchor=W)
        # self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        # self.temperatureLbl.pack(side=LEFT, anchor=N)
        # self.iconLbl = Label(self.degreeFrm, bg="black")
        # self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        # self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        # self.currentlyLbl.pack(side=TOP, anchor=W)
        # self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.forecastLbl.pack(side=TOP, anchor=W)
        # self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        # self.locationLbl.pack(side=TOP, anchor=W)

    def config_update(self):
        config = json.load(open("./components/parameters.json", "rb"))
        self.location = config['location']
        self.units = config['display_type']['units']
        self.apikey = config['apikeys']['openweather']

    @staticmethod
    def get_time(unix_utc):
        return datetime.utcfromtimestamp(int(unix_utc)).strftime('%Y-%m-%d %H:%M:%S')

    def get_weather(self):
        success_code = -1
        try:
            # get weather
            weather_req_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={self.location['lat']}&\
                lon={self.location['long']}&\
                units={self.units}&\
                exclude=hourly,minutely&\
                appid={self.apikey}"

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)
            print(weather_obj)
            quit()

            self.current = {
            'curr_temp' : weather_obj['current']['temp'],
            'curr_sunrise' : get_time(weather_obj['current']['sunrise']),
            'curr_sunset' : get_time(weather_obj['current']['sunset']),
            'curr_feelslike' : weather_obj['current']['feel_like'],
            'curr_humidity' : weather_obj['current']['humidity'],
            'curr_uv' : weather_obj['current']['uvi'],
            'curr_visibility' : weather_obj['current']['visibility'],
            'curr_windspeed' : weather_obj['current']['wind_speed'],
            'curr_windgust' : weather_obj['current']['wind_gust'],
            'curr_weather' : weather_obj['current']['weather'] # id, main, desc, icon
            }

            self.forecast = {
                'forecast7_temp' : weather_obj['daily']['temp']['day'],
                'forecast7_feelslike' : weather_obj['daily']['feels_like']['day'],
                'forecast7_weather' : weather_obj['daily']['weather'] # id, main, desc, icon
            }

            self.alerts = {
                'alerts_event' : weather_obj['alerts']['event'],
                'alerts_start' : get_time(weather_obj['alerts']['start']),
                'alerts_end' : get_time(weather_obj['alerts']['end'])
            }

            success_code = 0

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")
            success_code = -1

        # self.after(600000, self.get_weather)
        return success_code

    def ask_weather(self):
        self.config_update()
        self.get_weather()

    def modify_icon(self):
        pass
                # if icon2 is not None:
            #     if self.icon != icon2:
            #         self.icon = icon2
            #         image = Image.open(icon2)
            #         image = image.resize((100, 100), Image.ANTIALIAS)
            #         image = image.convert('RGB')
            #         photo = ImageTk.PhotoImage(image)

            #         self.iconLbl.config(image=photo)
            #         self.iconLbl.image = photo
            # else:
            #     # remove image
            #     self.iconLbl.config(image='')

if __name__ == "__main__":
    w = WeatherFunc()
    w.ask_weather() 