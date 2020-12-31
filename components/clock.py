# import modules
from tkinter import *  
import time, pickle

xlarge_text_size = 66
large_text_size = 48
medium_text_size = 28
small_text_size = 18
xsmall_text_size = 10
BG_COLOR = 'black'#'#D9B382'

class Clock:
    def __init__(self, parent, fdate):

        self.mainframe = Frame(parent, bg=BG_COLOR)
        self.mainframe.grid(column=2, row=1, sticky=(N, W, E, S))
        # self.current = Frame(self.mainframe, bg=BG_COLOR)
        # self.current.grid(column=1, row=1, sticky=(N, W))
        self.current_time = Label(self.mainframe, font=('Helvetica', xlarge_text_size), fg="white", bg=BG_COLOR)
        self.current_time.grid(column=1, row=1, sticky=(N))
        self.time = ''
        self.date = fdate
        self.fulldate = Label(self.mainframe, text = fdate, font=('Helvetica', medium_text_size), fg="white", bg=BG_COLOR)
        self.fulldate.grid(column=1, row=2, sticky=(N))

        self.ticker() # start clock!

    def ticker(self):
        new_time = time.strftime('%I:%M %p') #hour in 24h format
        new_date = time.strftime('%A %b %d %Y')
        self.time = new_time if new_time != self.time else self.time
        self.current_time.config(text=self.time)
        self.date = new_date if new_date != self.date else self.date
        self.fulldate.config(text=self.date)
        self.current_time.after(200, self.ticker)

def test_table():
    data = pickle.load(open("data.pickle","rb"))['current']['dt']
    print(data)
    win = Tk()
    w: Clock = Clock(win, data)
    win.mainloop()
if __name__ == "__main__":
    test_table()   