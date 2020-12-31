# import modules
from tkinter import *  
import time, pickle, json

class Clock:
    def __init__(self, parent:Tk, fdate:str) -> None:
        '''
        Initializing the time/date module
        Starts the clock
        Parameters
        ----------
        self : (Clock object) containing parameters to fill/update with clock data
        parent : (Tk object) main window
        fdate : (str) string representation of current date

        Return
        ------
        None
        '''
        self.config_update()
        self.mainframe = Frame(parent, bg=self.BG_COLOR)
        self.mainframe.grid(column=2, row=1, sticky=(N, W, E, S))

        self.current_time = Label(self.mainframe, font=('Helvetica', int(self.xlarge_text_size*0.8)), fg=self.FG_COLOR, bg=self.BG_COLOR)
        self.current_time.grid(column=1, row=1, sticky=(N))
        self.time = ''
        self.date = fdate
        self.fulldate = Label(self.mainframe, text = fdate, font=('Helvetica', self.medium_text_size), fg=self.FG_COLOR, bg=self.BG_COLOR)
        self.fulldate.grid(column=1, row=2, sticky=(N))

        self.ticker() # start clock!

    def ticker(self) -> None:
        ''' Updates clock time and date if there are any changes

        Parameters
        ----------
        self : (Clock object) containing parameters to fill/update with clock data

        Return
        ------
        None
        '''
        new_time = time.strftime('%I:%M %p') #hour in 24h format
        new_date = time.strftime('%A %b %d %Y')
        self.time = new_time if new_time != self.time else self.time
        self.current_time.config(text=self.time)
        self.date = new_date if new_date != self.date else self.date
        self.fulldate.config(text=self.date)
        self.current_time.after(200, self.ticker)
    
    def config_update(self) -> None:
        ''' Transfers relevant content from config file into object's parameters

        Parameters
        ----------
        self : (Clock object) containing parameters to fill/update with clock data

        Return
        ------
        None
        '''
        
        config = json.load(open("./components/parameters.json", "rb"))
        self.FG_COLOR = config['colors']['FG_COLOR']
        self.BG_COLOR = config['colors']['BG_COLOR']
        self.xlarge_text_size = config['font_size']['xlarge_text_size']
        self.large_text_size = config['font_size']['large_text_size']
        self.medium_text_size= config['font_size']['medium_text_size']
        self.small_text_size= config['font_size']['small_text_size']
        self.xsmall_text_size= config['font_size']['xsmall_text_size']


def test_table():
    data = pickle.load(open("data.pickle","rb"))['current']['dt']
    print(data)
    win = Tk()
    w: Clock = Clock(win, data)
    win.mainloop()
if __name__ == "__main__":
    test_table()   