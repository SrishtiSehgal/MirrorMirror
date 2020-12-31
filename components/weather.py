# import modules
from tkinter import *  
import requests, json, traceback, datetime, pytz, pickle
from PIL import Image, ImageTk

DEGREE_SYMBOL = u'\N{DEGREE SIGN}'
MAIN_KEYS = ['current','daily','alerts']
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18
xsmall_text_size = 10
BG_COLOR = 'black'#'#D9B382'
FORECAST_IMG = (100,100)
CURRENT_IMG = (200,200)

class WeatherFunc:
    ''' Creates and maintains the weather module on the smart mirror '''
    
    def __init__(self, parent, *args, **kwargs):
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

        # weather module
        self.mainframe = Frame(parent, bg=BG_COLOR)
        self.mainframe.grid(column=1, row=1, sticky=(N, W, E, S))
        self.current = Frame(self.mainframe, bg=BG_COLOR)
        self.current.grid(column=1, row=1, sticky=(N, W))
        
        # current temp submodule
        self.current_temp = Label(self.current, font=('Helvetica', xlarge_text_size), fg="white", bg=BG_COLOR)
        self.current_temp.grid(column=1, row=1, sticky=(N), padx=50)
        self.current_icon = Label(self.current, bg=BG_COLOR)
        self.current_icon.grid(column=2, row=1, sticky=(N,W,E,S))
        self.current_feelslike = Label(self.current,  font=('Helvetica', medium_text_size), fg="white", bg=BG_COLOR)
        self.current_feelslike.grid(column=1, row=2, sticky=(N))
        self.current_weather = Label(self.current,  font=('Helvetica', small_text_size), fg="white", bg=BG_COLOR)
        self.current_weather.grid(column=1, row=3, sticky=(N))
        
        # other current temp info submodule 
        self.current_humidity = Label(self.current,  font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.current_humidity.grid(column=4, row=2, sticky=(N, W,S,E))
        self.current_uvi = Label(self.current,  font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.current_uvi.grid(column=4, row=3, sticky=(N))
        self.current_visibility = Label(self.current,  font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.current_visibility.grid(column=5, row=2, sticky=(N, W,S,E))
        self.current_wind_speed = Label(self.current,  font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.current_wind_speed.grid(column=5, row=3, sticky=(N))
    
        # sunrise/sunset info
        self.sun = Canvas(self.current, width=70, height=60, bg=BG_COLOR,  bd=0, highlightthickness=0, relief='ridge')
        self.sun.grid(column=2, row=2, rowspan=2)

        # forecast submodule
        self.forecast = Frame(self.mainframe, bg=BG_COLOR)
        self.forecast.grid(column=1, row=5, sticky=(S))
        self.fd = ForecastDisplay()

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

    @staticmethod
    def get_image(pic_ID:str, s:tuple=FORECAST_IMG) -> Image:

        # root = Tk()
        # root.title("display a website image")
        # a little more than width and height of image
        # w = 200
        # h = 200
        # x = 80
        # y = 100
        # # use width x height + x_offset + y_offset (no spaces!)
        # root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        if pic_ID is not 'XXX':
            response = requests.get(f"http://openweathermap.org/img/wn/{pic_ID}@2x.png", stream=True)
        else:
            response = requests.get("https://tce-live2.s3.amazonaws.com/media/media/thumbnails/da1aa98a-4de3-42e2-bbef-9a734c03ff5e.jpg", stream=True)
        image = Image.open(response.raw)
        image = image.resize(s, Image.ANTIALIAS)
        # image = image.convert('1')
        # photo = ImageTk.PhotoImage(image)
        # self.iconLbl.config(image=photo)
        # self.iconLbl.image = photo

        # create a white canvas
        # cv = Canvas(bg='white')
        # cv.pack(side='top', fill='both', expand='yes')

        # put the image on the canvas with
        # cv.create_image(10, 10, image=photo, anchor='nw') # create_image(xpos, ypos, image, anchor)
        # root.mainloop()

        return image

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
        if True:#input('Load?')=='Y':
            self.load_data()
        else:
            self.get_weather()
            self.data_cleanup()
            self.save_data()
        self.create_visual()

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
            # current - weather: choose primary icon image and combine all descriptions,
            #         - dt: convert utc unix time into string representation (with day of week),
            #         - sunrise: convert utc unix time into string representation (keep hour and min only),
            #         - sunset: convert utc unix time into string representation (keep hour and min only)
            #         - temp, feels_like: convert to string and add degree sign
            #         - humidity: convert to string and add percent sign
            #         - visibility: convert to string and convert to km (show units)
            #         - wind_speed: convert to string and convert to km/hr (show units)

            self.weather_data['current']['weather'] = {
                'icon': WeatherFunc.get_image(self.weather_data['current']['weather'][0]['icon'], CURRENT_IMG), 
                'description':', '.join(
                    [condition['description'] for condition in self.weather_data['current']['weather']]
                )
            }
            self.weather_data['current']['temp'] =  str(round(self.weather_data['current']['temp']))+DEGREE_SYMBOL
            self.weather_data['current']['feels_like'] =  str(round(self.weather_data['current']['feels_like']))+DEGREE_SYMBOL
            self.weather_data['current']['humidity'] =  str(round(self.weather_data['current']['humidity']))+'%'
            self.weather_data['current']['uvi'] =  str(round(self.weather_data['current']['uvi']))
            self.weather_data['current']['visibility'] =  str(round(self.weather_data['current']['visibility']/1000))+' km'
            self.weather_data['current']['wind_speed'] =  str(round(self.weather_data['current']['wind_speed']*3600/1000))+' km/hr'
            self.weather_data['current']['dt'] = WeatherFunc.reformat_time(self.weather_data['current']['dt'], '%A %B %d %Y')
            self.weather_data['current']['sunrise'] = WeatherFunc.reformat_time(self.weather_data['current']['sunrise'], '%H:%M')
            self.weather_data['current']['sunset'] = WeatherFunc.reformat_time(self.weather_data['current']['sunset'], '%H:%M')
        except KeyError:
            print('current-weather might be missing data')
            success_code = 1
        except Exception as e2:
            print (f"New error! {e2} @ current-weather")
            success_code = -1
        
        # daily - remove [0] entry (current day)
        #       - feels_like: choose day temp for each day, 
        #       - temp: choose day temp for each day, 
        #       - weather: choose primary icon image and combine all descriptions for each day
        #       - dt: convert utc unix time into string representation (day of week only)
        #       - temp, feels_like: convert to string and add degree sign
        self.weather_data['daily'] = self.weather_data['daily'][1:]
        for day in range(len(self.weather_data['daily'])):
            try:
                self.weather_data['daily'][day]['dt'] = WeatherFunc.reformat_time(self.weather_data['daily'][day]['dt'], '%a')
                self.weather_data['daily'][day]['temp'] = str(round(self.weather_data['daily'][day]['temp']['day']))+DEGREE_SYMBOL
                self.weather_data['daily'][day]['feels_like'] = str(round(self.weather_data['daily'][day]['feels_like']['day']))+DEGREE_SYMBOL
                self.weather_data['daily'][day]['weather'] = {
                    'icon': WeatherFunc.get_image(self.weather_data['daily'][day]['weather'][0]['icon']), 
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

        print(self.weather_data)
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

    def create_visual(self) -> None:
        img = self.weather_data['current']['weather']['icon']
        if img is None:
            img = WeatherFunc.get_image('XXX', (200,200))
        w, h = img.size
        left = w/4
        right = 3*w/4
        upper = h/4
        lower = 3*h/4
        img = img.crop([ left, upper, right, lower])
        photo = ImageTk.PhotoImage(img)
        self.current_icon.config(image=photo)
        self.current_icon.image = photo

        self.current_temp.config(text=self.weather_data['current']['temp'])
        self.current_feelslike.config(text=self.weather_data['current']['feels_like'])
        self.current_weather.config(text=self.weather_data['current']['weather']['description'])

        self.current_humidity.config(text='Humidity:'+self.weather_data['current']['humidity'])
        self.current_uvi.config(text='UV:'+str(self.weather_data['current']['uvi']))
        self.current_visibility.config(text='Visibility:'+self.weather_data['current']['visibility'])
        self.current_wind_speed.config(text='Wind Speed:'+self.weather_data['current']['wind_speed'])

        l1 = self.sun.create_text(20, 20, text=self.weather_data['current']['sunrise'], font=("Purisa", xsmall_text_size), fill="orange", tag="l1")
        l2 = self.sun.create_text(20, 40, text=self.weather_data['current']['sunset'], font=("Purisa", xsmall_text_size), fill="grey", tag="l2")
        self.sun.create_line(0, (self.sun.coords(l1)[1]+self.sun.coords(l2)[1])/2, self.sun.coords(l1)[0]*2, ( self.sun.coords(l1)[1]+self.sun.coords(l2)[1])/2, fill="white")

        self.fd.populate_days(self.forecast, self.weather_data['daily'])

    def save_data(self):
        pickle.dump(self.weather_data, open("data.pickle","wb"),pickle.HIGHEST_PROTOCOL)

    def load_data(self):
        self.weather_data = pickle.load(open("data.pickle","rb"))
        print(self.weather_data)

class ForecastDisplay:
    '''
        Wed    Thurs    Fri     Sat     Sun ...
        Pic     Pic     Pic     Pic     Pic
        Desc    Desc    Desc    Desc    Desc
        Temp    Temp    Temp    Temp    Temp
        Feels   Feels   Feels   Feels   Feels
    '''
    def __init__(self):

        # assume 7 days of forecast info
        self.days = {
            'day1':None,
            'day2':None,
            'day3':None,
            'day4':None,
            'day5':None,
            'day6':None,
            'day7':None
        }

    def populate_days(self, root, data):
        for d in range(len(data)):
            self.days['day'+str(d+1)] = WeatherPanel(root, d+1, 1)
            self.days['day'+str(d+1)].dataloader(data[d])
class WeatherPanel:
    def __init__(self, parent, col_pos, row_pos):
        self.root = Frame(parent, bg=BG_COLOR)
        self.root.grid(column=col_pos, row=row_pos, sticky=(N, W, E, S))

        self.day = Label(self.root, font=('Helvetica', small_text_size), fg="white", bg=BG_COLOR)
        self.day.grid(column=1, row=1, sticky=(N))
        
        self.pic = Label(self.root, bg=BG_COLOR)
        self.pic.grid(column=1, row=2, sticky=(N))

        self.desc = Label(self.root, font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.desc.grid(column=1, row=3, sticky=(N))

        self.temp = Label(self.root, font=('Helvetica', small_text_size), fg="white", bg=BG_COLOR)
        self.temp.grid(column=1, row=4, sticky=(N))

        self.feels_like = Label(self.root, font=('Helvetica', xsmall_text_size), fg="white", bg=BG_COLOR)
        self.feels_like.grid(column=1, row=5, sticky=(N))

    def dataloader(self,data):
        self.day.config(text= data['dt'])
        
        self.desc.config(text=data['weather']['description'])
        
        self.temp.config(text=data['temp'])

        self.feels_like.config(text=data['feels_like'])

        img = data['weather']['icon']
        if img is None:
            img = WeatherFunc.get_image('XXX', (200,200))
        photo = ImageTk.PhotoImage(img)
        self.pic.config(image=photo)
        self.pic.image = photo

def test_table():
    data = pickle.load(open("data.pickle","rb"))['daily']
    print(data)
    win = Tk()
    w: WeatherFunc = WeatherFunc(win)
    w.ask_weather()
    # win.columnconfigure(0, weight=1)
    # win.rowconfigure(0, weight=1)
    # fd = ForecastDisplay()
    # fd.populate_days(win, data)
    win.mainloop()

def local_test():
    # w: WeatherFunc = WeatherFunc()
    # w.ask_weather()
    # print(WeatherFunc.reformat_time(1609296052, '%a %d'))
    # WeatherFunc.get_image('04d')
    # del w
    pass

if __name__ == "__main__":
    test_table()