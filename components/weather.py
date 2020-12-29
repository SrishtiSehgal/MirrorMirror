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
from collections import defaultdict

# class WeatherFunc(Frame):
class WeatherFunc:
    ''' Creates and maintains the weather module on the smart mirror '''
    DEGREE_SYMBOL = u'\N{DEGREE SIGN}'
    MAIN_KEYS = ['current','forecast','alerts']

    # def __init__(self, parent, *args, **kwargs):
        # Frame.__init__(self, parent, bg='black')
    def __init__(self):
        '''
        Initialize object parameters in prep to be updated with other methods
        
        Parameters
        ----------
        self : (WeatherFunc object) containing parameters to initialize
        
        Return
        ------
        None
        '''
        self.location = '' # dict
        self.apikey = ''
        self.units = ''

        self.weather_data = d1 = {key:{} for key in MAIN_KEYS}
        self.weather_data['current'] = {
                                        'temp' : '',
                                        'sunrise' : '',
                                        'sunset' : '',
                                        'feel_like' : '',
                                        'humidity' : '',
                                        'uvi' : '',
                                        'visibility' : '',
                                        'wind_speed' : '',
                                        'wind_gust' : '',
                                        'weather' : {}
        }

        self.weather_data['forecast'] = {
                                        'temp' : {'day':''},
                                        'feel_like' : {'day':''},
                                        'weather' : {}
        }

        self.weather_data['alerts'] = {
                                        'event' : '',
                                        'start' : '',
                                        'end' : ''
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

    def config_update(self) -> None:
        ''' Transfers relevant content from config file into object's parameters

        Parameters
        ----------
        self : (WeatherFunc object) containing parameters to fill/update with weather data

        Return
        ------
        None
        '''
        
        config = json.load(open("./components/parameters.json", "rb"))
        self.location = config['location']
        self.units = config['display_type']['units']
        self.apikey = config['apikeys']['openweather']

    @staticmethod
    def reformat_time(unix_utc:str) -> str:
        '''
        Convert unix UTC time into a datetime object

        Parameters
        ----------
        unix_utc : (string) unix UTC time

        Return
        ------
        formatted_time : (string) converted from datetime object into the form 'YYYY-MM-DD HH:MM:SS'
        '''
        formatted_time = datetime.utcfromtimestamp(int(unix_utc)).strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time

    def get_weather(self) -> int:
        '''
        Make a GET request using OpenWeatherMap API to gather current and future weather data

        Parameters
        ----------
        self : (WeatherFunc object) containing parameters to fill/update with weather data

        Return
        ------
        success_code : (int) code 0 for successful request and update, -1 for bad request
        '''
        success_code = -1
        try:
            # get weather
            weather_req_url = f"https://api.openweathermap.org/data/2.5/onecall?\
                lat={self.location['lat']}&\
                lon={self.location['long']}&\
                units={self.units}&\
                exclude=hourly,minutely&\
                appid={self.apikey}"

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)
            print(weather_obj)

            if not all(key in weather_obj for key in MAIN_KEYS):
                print('API call failed')
                success_code = -1
                return success_code

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")
            success_code = -1
            return success_code

        success_code = self.add_to_object(weather_obj)
        if success_code == -1:
            print(f"Unknown error. Cannot get weather.")
            return success_code
        if success_code == 1:
            print(f"Possible issue in data collection...")
            return success_code

        # self.after(600000, self.get_weather)
        return success_code

    def ask_weather(self) -> None:
        '''
        Update object parameters using config file and make the call to get new data

        Parameters
        ----------
        self : (WeatherFunc object) containing parameters to fill/update with weather data

        Return
        ------
        None
        '''
        self.config_update()
        self.get_weather()

    def modify_icon(self) -> None:
        '''
        Modify current and forecasted weather to combine descriptions and to choose one icon

        Parameters
        ----------
        self : (WeatherFunc object) containing weather data

        Return
        ------
        None
        '''
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

    def add_to_object(self, weather_obj:dict) -> int:
        '''
        Add current and forecasted weather data to object, and handle errors

        Parameters
        ----------
        self : (WeatherFunc object) as an empty data container
        weather_obj : (dict) contains collected weather data

        Return
        ------
        success_code : (int) 0: no issues, 1: possible issue, -1: unhandled error 
        '''
        success_code = 0
        for mainkey in MAIN_KEYS:
            for key in self.weather_data[mainkey]:
                try:
                    data = weather_obj[mainkey][key]
                    if len(data) == 0:
                        print(f"No data @ {mainkey}:{key}")
                    else:
                        self.weather_data[mainkey][key] = data
                except KeyError as e:
                    print('API call failed or key has no data')
                    print(f'Error {e} @ {mainkey}:{key}')
                    success_code = 1
                    continue
                except Exception as e2:
                    print (f"New error! {e2} @ {mainkey}:{key}")
                    success_code = -1
        return success_code
            

def local_test():
    w: WeatherFunc = WeatherFunc()
    w.ask_weather()
    del w

if __name__ == "__main__":
    local_test()