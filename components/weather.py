# import modules
from tkinter import *  
import requests, json, traceback, datetime, pytz
from PIL import Image, ImageTk
from collections import defaultdict

DEGREE_SYMBOL = u'\N{DEGREE SIGN}'
MAIN_KEYS = ['current','daily','alerts']
# class WeatherFunc(Frame):
class WeatherFunc:
    ''' Creates and maintains the weather module on the smart mirror '''
    
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
        self.location = ''
        self.apikey = ''
        self.units = ''

        self.weather_data = {}
        self.weather_data['current'] = {
                                        'dt' : '',
                                        'temp' : '',
                                        'sunrise' : '',
                                        'sunset' : '',
                                        'feels_like' : '',
                                        'humidity' : '',
                                        'uvi' : '',
                                        'visibility' : '',
                                        'wind_speed' : '',
                                        'weather' : {}
        }

        self.weather_data['daily'] = []

        self.weather_data['alerts'] = []

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
    def reformat_time(unix_utc:str, final_format:str='%A %b %d %Y %H:%M:%S') -> str:
        '''
        Convert unix UTC time into a datetime object

        Parameters
        ----------
        unix_utc : (str) unix UTC time
        final_format : (str) parameters indicating which parts of time related information to show 
                (default = '%A %m %d %Y %H:%M:%S')
                'Y' - year, 'm'/'b'/'B' - month, 'd' - date, 'A'/'a' - day, 'H' - hour, 'M' - minute, 'S' - second

        Return
        ------
        formatted_time : (string) time information shown as the partial or full form of '(day) DD-MM-YYYY HH:MM:SS'
        '''
        full_formatted_time = datetime.datetime.utcfromtimestamp(int(unix_utc)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
        return full_formatted_time.strftime(final_format)

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
            print(self.apikey)
            # get weather
            weather_req_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={self.location['lat']}&lon={self.location['long']}&units={self.units}&exclude=hourly,minutely&appid={self.apikey}"
            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            if not all(key in weather_obj for key in MAIN_KEYS[:-1]): # not always an alert available
                print('API call failed')
                success_code = -1
                return success_code

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")
            success_code = -1
            return success_code

        success_code = self.add_to_object(weather_obj)
        success_code = self.data_cleanup()
        print(self.weather_data)
        if success_code == -1:
            print(f"Unknown error. Cannot get weather.")
            return success_code
        elif success_code == 1:
            print(f"Possible issue in data collection...")
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

    def data_cleanup(self) -> int:
        '''
        Modify current and forecasted weather to combine/simplify descriptions
        Parameters
        ----------
        self : (WeatherFunc object) containing weather data

        Return
        ------
        success_code : (int) code 0 for successful request and update, -1 for bad request, 1 for missing data
        '''
        success_code = 0
        try:
            # current - weather: choose primary icon and combine all descriptions,
            #         - dt: convert utc unix time into string representation (with day of week),
            #         - sunrise: convert utc unix time into string representation (keep hour and min only),
            #         - sunset: convert utc unix time into string representation (keep hour and min only)
            #         - temp, feels_like: convert to string and add degree sign
            #         - humidity: convert to string and add percent sign
            #         - visibility: convert to string and convert to km (show units)
            #         - wind_speed: convert to string and convert to km/hr (show units)
            self.weather_data['current']['weather'] = {
                'icon':self.weather_data['current']['weather'][0]['icon'], 
                'description':', '.join(
                    [condition['description'] for condition in self.weather_data['current']['weather']]
                    )
                }
            self.weather_data['current']['temp'] =  str(self.weather_data['current']['temp'])+DEGREE_SYMBOL
            self.weather_data['current']['feels_like'] =  str(self.weather_data['current']['feels_like'])+DEGREE_SYMBOL
            self.weather_data['current']['humidity'] =  str(self.weather_data['current']['humidity'])+'%'
            self.weather_data['current']['visibility'] =  str(self.weather_data['current']['visibility']/1000)+' km'
            self.weather_data['current']['wind_speed'] =  str(self.weather_data['current']['wind_speed']*3600/1000)+' km/hr'
            self.weather_data['current']['dt'] = WeatherFunc.reformat_time(self.weather_data['current']['dt'], '%A %B %d %Y')
            self.weather_data['current']['sunrise'] = WeatherFunc.reformat_time(self.weather_data['current']['sunrise'], '%H:%M')
            self.weather_data['current']['sunset'] = WeatherFunc.reformat_time(self.weather_data['current']['sunset'], '%H:%M')
        except KeyError:
            print('current-weather might be missing data')
            success_code = 1
        except Exception as e2:
            print (f"New error! {e2} @ current-weather")
            success_code = -1
        
        # daily - feels_like: choose day temp for each day, 
        #       - temp: choose day temp for each day, 
        #       - weather: choose primary icon and combine all descriptions for each day
        #       - dt: convert utc unix time into string representation (keep day of week and number only)
        #       - temp, feels_like: convert to string and add degree sign
        for day in range(len(self.weather_data['daily'])):
            try:
                self.weather_data['daily'][day]['dt'] = WeatherFunc.reformat_time(self.weather_data['daily'][day]['dt'], '%a %d')
                self.weather_data['daily'][day]['temp'] = str(self.weather_data['daily'][day]['temp']['day'])+DEGREE_SYMBOL
                self.weather_data['daily'][day]['feels_like'] = str(self.weather_data['daily'][day]['feels_like']['day'])+DEGREE_SYMBOL
                self.weather_data['daily'][day]['weather'] = {
                    'icon': self.weather_data['daily'][day]['weather'][0]['icon'], 
                    'description':', '.join(
                        [condition['description'] for condition in self.weather_data['daily'][day]['weather']]
                    )
                }
            except KeyError:
                print(f'daily-temp,feels_like or weather @ index {day} might be missing data')
                success_code = 1
            except Exception as e2:
                print (f"New error! {e2} @ index {day} for daily-temp,feels_like or weather")
                success_code = -1
        # alerts : - start: convert utc unix time into string representation
        #          - end: convert utc unix time into string representation
        for alert in range(len(self.weather_data['alerts'])):
            try:
                self.weather_data['alerts'][alert]['start'] = WeatherFunc.reformat_time(self.weather_data['alerts'][alert]['start'], '%a %b %d %Y %H:%M:%S')
                self.weather_data['alerts'][alert]['end'] = WeatherFunc.reformat_time(self.weather_data['alerts'][alert]['end'], '%a %b %d %Y %H:%M:%S')
            except KeyError:
                print(f'alerts-start or end @ index {alert} might be missing data')
                success_code = 1
            except Exception as e2:
                print (f"New error! {e2} @ index {alert} for alerts-start or end")
                success_code = -1
        return success_code

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
            if mainkey != 'current':
                try:
                    self.weather_data[mainkey] = [{k:v for k,v in day.items() if k in ['temp','feels_like','weather','dt', 'event','start','end']} for day in weather_obj[mainkey]]
                except KeyError:
                    print(f'{mainkey} might be missing data')
                    success_code = 1
                    continue
                except Exception as e2:
                    print (f"New error! {e2} @ {mainkey}")
                    success_code = -1
            else:
                try:
                    self.weather_data[mainkey] = {k:v for k,v in weather_obj[mainkey].items() if k in self.weather_data[mainkey]}
                except KeyError:
                    print(f'{mainkey} might be missing data')
                    success_code = 1
                    continue
                except Exception as e2:
                    print (f"New error! {e2} @ {mainkey}")
                    success_code = -1
        return success_code

def local_test():
    w: WeatherFunc = WeatherFunc()
    w.ask_weather()
    print(WeatherFunc.reformat_time(1609296052, '%a %d'))
    del w

if __name__ == "__main__":
    local_test()