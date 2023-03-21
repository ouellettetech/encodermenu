from picolcd.picolcd import *

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

    def initMenu(self, bgColor, borderColor, textColor):
        self.LCD.fill(bgColor)
        self.LCD.show()
        self.textColor = textColor
        self.LCD.hline(10,10,220,borderColor)
        self.LCD.hline(10,125,220,borderColor)
        self.LCD.vline(10,10,115,borderColor)
        self.LCD.vline(230,10,115,borderColor)
        self.LCD.text("OK",210,15,self.textColor)
        self.LCD.text("BACK",195,110,self.textColor)
                
    def display(self,cursor, line1,line2,line3,line4,line5):
        self.LCD.text("   "+line1,90,20,self.textColor)
        self.LCD.text("   "+line2,90,40,self.textColor)
        self.LCD.text("   "+line3,90,60,self.textColor)
        self.LCD.text("   "+line4,90,80,self.textColor)
        self.LCD.text("   "+line5,90,100,self.textColor)
        self.LCD.text(" * ",90,((cursor+1)*20),self.textColor)
        self.LCD.show()
        
    def initKeys(self,select,back,up,down):
        self.select = select
        self.back = back
        self.up = up
        self.down = down
    
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
                    self.LCD.fill_rect(37,35,20,20,self.LCD.red)
                    print("UP")
                    self.currentMenuItem-=1
                    self.currentMenuItem=self.currentMenuItem%self.numMenuItems
                    print(self.currentMenuItem)
                    self.lastButton = 2
            else :
                if(self.lastButton == 2):
                    self.lastButton = -1
                self.LCD.fill_rect(37,35,20,20,self.LCD.white)
                self.LCD.rect(37,35,20,20,self.LCD.red)
                
            if(self.down.value() == 0):#下
                if(self.lastButton != 5):
                    self.LCD.fill_rect(37,85,20,20,self.LCD.red)
                    print("DOWN")
                    self.currentMenuItem+=1
                    self.currentMenuItem=self.currentMenuItem%self.numMenuItems
                    print(self.currentMenuItem)
                    self.lastButton = 5
            else :
                if(self.lastButton == 5):
                    self.lastButton = -1
                self.LCD.fill_rect(37,85,20,20,self.LCD.white)
                self.LCD.rect(37,85,20,20,self.LCD.red)
                
            self.LCD.show()

