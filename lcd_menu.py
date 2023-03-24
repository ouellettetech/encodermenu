from picolcd.picolcd import *

import uasyncio as asyncio

#!!!!!!!!!----------------

# There are 5 hardware functions
# 1. Display text
# 2. Read button or switch for click_event
# 3. Read value from encoder for scroll event
# 4. Setup the encoder, so that encoder values are sensible
# 5. Set a flashing led as a heart beat for main loop (optional)
# If you get these functions to work there should be no hardware

class LCD_Menu:
    def __init__(self, LCD:LCD_1inch14):
        self.currentMenuItem=0
        self.numMenuItems=4
        self.lastButton=-1
        self.LCD = LCD
        self.line1 = "title"
        self.line2 = "line1"
        self.line3 = "line2"
        self.line4 = "line3"
        self.line5 = "line4"
        #================================
        self.stack = []  # For storing position in menu
        self.current =  None  # The b=object currently handling events
        self.menu_data = {} # For getting data out of the menu
        self.task = None   # This holds a task for asyncio

    def initMenu(self, bgColor, borderColor, textColor):
        self.bgColor = bgColor
        self.borderColor = borderColor
        self.textColor = textColor
        self.LCD.fill(bgColor)
        self.LCD.show()
        self.LCD.hline(10,10,220,borderColor)
        self.LCD.hline(10,125,220,borderColor)
        self.LCD.vline(10,10,115,borderColor)
        self.LCD.vline(230,10,115,borderColor)
        self.LCD.text("OK",210,15,self.textColor)
        self.LCD.text("BACK",195,110,self.textColor)
                
    def display(self,cursor, line1,line2,line3,line4,line5):
        self.LCD.fill_rect(11,11,180,100,self.bgColor)
        self.LCD.text("   "+line1,10,20,self.textColor)
        self.LCD.text("   "+line2,10,40,self.textColor)
        self.LCD.text("   "+line3,10,60,self.textColor)
        self.LCD.text("   "+line4,10,80,self.textColor)
        self.LCD.text("   "+line5,10,100,self.textColor)
        self.LCD.text(" * ",10,((cursor+2)*20),self.textColor)
        self.LCD.show()
        
    def setCurrentMenu(self, line1,line2,line3,line4,line5):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.line4 = line4
        self.line5 = line5
        
    def initKeys(self,select,back,up,down):
        self.select = select
        self.back = back
        self.up = up
        self.down = down
    
    #Little utility function to avoid some module definitions
    def set_data(self, key,value):
        self.menu_data[key]=value
        print ('setting',self.menu_data)
        
    #This is taken from Peter Hinch's tutorial
    def set_global_exception():
        def handle_exception(loop, context):
            import sys
            sys.print_exception(context["exception"])
            sys.exit()
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_exception)

    def run(self):
        while(1):
            if(self.select.value() == 0):
                if(self.lastButton != 0):
                    self.LCD.rect(208,12,20,20,self.LCD.green)
                    print("A")
                    self.lastButton = 0
            else :
                if(self.lastButton == 0 ):
                    self.lastButton = -1
                self.LCD.rect(208,12,20,20,self.LCD.white)
                
                
            if(self.back.value() == 0):
                if(self.lastButton != 1):
                    self.LCD.rect(193,103,35,20,self.LCD.green)
                    print("B")
                    self.lastButton = 1
            else :
                if(self.lastButton == 1):
                    self.lastButton = -1
                self.LCD.rect(193,103,35,20,self.LCD.white)

            if(self.up.value() == 0):#上
                if(self.lastButton != 2):
                    print("UP")
                    self.currentMenuItem-=1
                    self.currentMenuItem=self.currentMenuItem%self.numMenuItems
                    print(self.currentMenuItem)
                    self.lastButton = 2
            else :
                if(self.lastButton == 2):
                    self.lastButton = -1
                
            if(self.down.value() == 0):#下
                if(self.lastButton != 5):
                    self.currentMenuItem+=1
                    self.currentMenuItem=self.currentMenuItem%self.numMenuItems
                    print(self.currentMenuItem)
                    self.lastButton = 5
            else :
                if(self.lastButton == 5):
                    self.lastButton = -1
            self.display(self.currentMenuItem,self.line1,self.line2,self.line3,self.line4,self.line5)
            self.LCD.show()

