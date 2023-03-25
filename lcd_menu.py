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
    def set_global_exception(self):
        def handle_exception(loop, context):
            import sys
            sys.print_exception(context["exception"])
            sys.exit()
        self.loop = asyncio.get_event_loop()
        self.loop.set_exception_handler(handle_exception) 
    
    #============================
    #loop related
        
        
    def mainloop(self):
        "An asynchronous main loop"
        self.set_global_exception()

        while True:
            self.step()
            #await self.step()
            
    def run_async(self, func):
        "run a function asynchronously"
        try:
            asyncio.run(func())
        finally:
            asyncio.new_event_loop()  # Clear retained state
            
    def run_menu(self):
        #convenience function so we dont need module references or global
        self.run_async(self.mainloop)


    # async def step():
    #     """Poll for scroll and switch events
    #     """
    #     global old_v,old_switch
    #     enc_v = value()
        
    #     if enc_v != old_v:
    #         current.on_scroll(enc_v)
    #         old_v = enc_v
            
    #     sw_v = button()
    #     if sw_v != old_switch:
    #         if sw_v:
    #             current.on_click()
    #         old_switch = sw_v
    #         await asyncio.sleep_ms(250)  # determined by trial error - debounces switch
    #     await asyncio.sleep(0)  #play nicely with others
        
    def step(self):
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

    #===============================
    #Menu navigation related

    def back(self):
        "go back up then menu by excuting this function"
        if len(self.stack) > 1:
        #the current menu is on the stack so we have to pop it off
            self.stack.pop()
        #Should be at least one item on stack. Set top of stack to current menu
        self.set_current( self.stack.pop())
           
    def set_current(self, obj):
        "always do this when we change the control object"
        self.stack.append(obj)
        self.current = obj
        self.current.on_current()

    #=======================
        # Task related

    def stop(self):
        "Convenience function for stopping tasks"
        """Our routine (neopixels in this case) is stored in a task.
        That allows us to cancel it"""
        try:
            self.task.cancel()
            self.task = None
        except:
            pass

 
    def make_task(self, func):
        "convenience function  for starting tasks"
        self.task = asyncio.create_task(func())


#=============================
#Object definitions for control objects
  
class Menu():
    "Show a menu on a tiny dispaly by turning a rotatry encoder"
    def __init__(self,menu,LCD, numberOfRows):
        self.menu = menu
        self.index = 0
        self.increment = 1
        
        
    def move_up(self):
        
    def on_scroll(self,value):
        "Just show the caption"
        self.index = value
        //display('', self.menu[value][0])
        
    def on_click(self):
        "Execute the menu item's function"
        (self.menu[self.index][1])()
    
    def on_current(self):
        "Set (and fix if necessary) the index"           
        set_encoder(self.index,0,len(self.menu)-1)        
        display('', self.menu[self.index][0])
        
        
class GetInteger():
    "Get an integer value by scrolling (or turning the encoder shaft)"
    global menu_data
    def __init__(self,low_v=0,high_v=100,increment=10, caption='plain',field='datafield',default=0):
        self.field = field  #for collecting data
        self.caption = caption #caption is fixed in get_integer mode
        self.increment = increment
        self.low_v = low_v
        self.high_v = high_v
        self.field = field
        self.default = default
        self.value = 0
        self.get_initial_value()

    def get_initial_value(self):
        #print('init value',self.value,self.increment,self.default,self.field)
        try:
            data_v = int(menu_data.get(self.field,self.default))
        except:
            data_v = 0
        data_v = self.low_v if data_v < self.low_v else data_v
        data_v = self.high_v if data_v > self.high_v else data_v
        encoder._value = data_v
        self.value = data_v
        
      
    def on_scroll(self,val):
        "Change the value displayed as we scroll"
        self.value = val
        display(self.caption,str(val * self.increment))
            
    def on_click(self):
        global menu_data
        "Store the displayed value and go back up the menu"
        menu_data[self.field]= self.value
        back()
        
    def on_current(self):
        "Make sure encode is set properly, set up data and display"
        self.get_initial_value()
        print('get_int',menu_data,self.value,encoder.value())
        set_encoder(self.value,self.low_v,self.high_v)
        display(self.caption,str(self.value * self.increment))


        
class Wizard():
    global stack
    """The wizard is a type of menu that  executes its own "leaves" in sequence"""
     
    def __init__(self,menu):

        self.menu      = menu
        self.index     = 0
        self.increment = 1       
        
    def on_scroll(self,value):
        "pass scroll event to leaf"
        self.device.on_scroll(value)
        
    def on_click(self):
        "exeute menu fn()->self.device. Fix stack and current"
        
        global current
        self.index += 1
        if self.index  > len(self.menu)-1:
            self.device.on_click()  #end of list so just go back
        else:
            self.device.on_click() #will pop ourself
            stack.append(self) #so put ourself back
            (self.menu[self.index][1])()#will push device
            self.device=current
            current=self
            stack.pop() #so we have to pop device
                
    def on_current(self):
        #Handle clicks to get entries in sequence
        #Pass scroll events on to the device.
        #(This requires fiddling the value of stack and current)
        global current
        self.index = 0 #always start at the beginning
        (self.menu[0][1])() #do menu function which puts a new object in current
        self.device = current #Now capture current
        current = self # restore current to self
        stack.pop() # the function pushes,so we have to pop()


        
        
class Info():
    "Show some information on the display.  "
    def __init__(self,message):
        self.message = message
        
    def on_scroll(self,val):
        pass
        
    def on_click(self):
        back()
        
    def on_current(self):
        oled.fill(0)
        for i,a in enumerate(self.message.split('\n')):
            oled.text(a,0,i*12)
        oled.show()
        
class Selection():
    "Return a string value from a menu like selection"
    def __init__(self,field,choices):
        global menu_data
       # print('selection field',field)
     #   print('menu data in init sel',menu_data)
        def str2tuple(x):
            if type (x) == str:
                return (x,x)
            else:
                return x
        self.field = field
        #If value is string convert to (string,string)
        self.choice =[str2tuple(x) for x in choices]
    #    print(self.choice)
        self.set_initial_value()
        
    def set_initial_value(self):
        global menu_data
        self.index = 0
        for i,a in enumerate(self.choice):
     #       print(self.field,a[1])
            if menu_data.get(self.field,'zzz') == a[1]:
            #   print('match')
               self.index = i
               break
               #break
     #   print('init index',self.choice[self.index])
    #    print(menu_data)

    

    def on_scroll(self,val):
        self.index = val
        display('',self.choice[self.index][0])
        
        
    def on_click(self):
        global menu_data
        menu_data[self.field] = self.choice[self.index][1]         
     #   print(menu_data)
        back()
        
    def on_current(self):
        self.set_initial_value()
        set_encoder(self.index,0,len(self.choice)-1)
        display('',self.choice[self.index][0])
        
#===================================
# Functions for defining menus
 
def  wrap_object(myobject):
    "wrap a list into a function so it can be set from within the menu"
    def mywrap():
        global current
        set_current(myobject)
    return mywrap

def wrap_menu(mymenulist):
    "wrap a list into a function so it can be set from within the menu"
    return wrap_object(Menu(mymenulist))

def wizard(mymenu):
    "Wrap a wizard list into a menu action"
    return wrap_object(Wizard(mymenu))

def info(string):
    "Wrap simple text output into menu"
    return wrap_object(Info(string))

def selection(field,mylist):
    "Wrap a selection into menu"
    return wrap_object(Selection(field,mylist))

def get_integer(low_v=0,high_v=100,increment=10, caption='plain',field='datafield',default='DEF'):
    "Wrap integer entry into menu"
    return wrap_object(GetInteger(low_v,high_v,increment, caption,field,default))


def dummy():
    "Just a valid dummy function to fill menu actions while we are developing"
    pass   

