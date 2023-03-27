

#import math
from machine import Pin
import sys
import time
from picolcd import LCD_1inch14

import uasyncio as asyncio

#from guimenu importMenu
#import _thread

#This section may need to be modified to suit your hardware
#from rotary_irq_pico  import RotaryIRQ
#import uasyncio as asyncio

#button = Pin(18,Pin.IN,Pin.PULL_DOWN)

class ControllerState():
    NONE = 0
    SELECT = 1
    BACK = 2
    SCROLL = 3

class Controller:
    button = Pin(15,Pin.IN,Pin.PULL_UP)
    back_button = Pin(17,Pin.IN,Pin.PULL_UP)

    keyUp = Pin(2 ,Pin.IN,Pin.PULL_UP)#UP
    keyCenter = Pin(3 ,Pin.IN,Pin.PULL_UP)#CENTER
    keyLeft = Pin(16 ,Pin.IN,Pin.PULL_UP)#LEFT
    keyDown = Pin(18 ,Pin.IN,Pin.PULL_UP)#DOWN
    keyRight = Pin(20 ,Pin.IN,Pin.PULL_UP)#RIGHT

    def __init__(self, default_value, min=0, max=100, swap_direction=False):
        self.current_value = default_value
        self.min_value = min
        self.max_value = max
        self.swap_direction = swap_direction #swap directions so thaUp goes down, but int values goes up.
        self.old_value = -1 #inital scroll values so first usage forces an event
        self.old_switch = self.button.value() # same for button
        self.old_up = self.keyUp.value() 
        self.old_down = self.keyDown.value()
        self.old_back = self.back_button.value()
        
    def value(self):
        print("Getting current Value: ")
        print(self.current_value)
        return self.current_value
    
    def set_value(self, value, min_value = 0,max_value = 100, swap_direction = False):
        self.current_value = value
        self.min_value = min_value
        self.max_value = max_value
        
    def get_state(self):
        """Poll for scroll and switch events
        """
        
        if(self.swap_direction):
            decrese = self.keyUp
            increase = self.keyDown
        else:
            increase = self.keyUp
            decrese = self.keyDown
        
        sw_v = self.button.value()
        if sw_v != self.old_switch:
            self.old_switch = sw_v
            if (sw_v == 0):
                print("button clicked")
                return ControllerState.SELECT
            
        up_v = increase.value()
        if up_v != self.old_up:
            self.old_up = up_v
            if (up_v == 0):
                print("up clicked")
                print(self.current_value)
                print(self.max_value)
                self.current_value+=1
                if(self.current_value>self.max_value):
                    self.current_value=self.min_value
                return ControllerState.SCROLL

        down_v = decrese.value()
        if down_v != self.old_down:
            self.old_down = down_v
            if (down_v == 0):
                print("down clicked")
                print(self.current_value)
                print(self.min_value)
                self.current_value-=1
                if(self.current_value<self.min_value):
                    self.current_value=self.max_value                
                return ControllerState.SCROLL

        back_v = self.back_button.value()
        if back_v != self.old_back:
            self.old_back = back_v
            if (back_v == 0):
                print("back clicked")
                return ControllerState.BACK
        return ControllerState.NONE    
        
led = Pin(25,Pin.OUT)

oled = LCD_1inch14()

led = Pin(25,Pin.OUT)

controller = Controller(0)

#!!!!!!!!!----------------

# There are 5 hardware functions
# 1. Display text
# 2. Read button or switch for click_event
# 3. Read value from encoder for scroll event
# 4. Setup the encoder, so that encoder values are sensible
# 5. Set a flashing led as a heart beat for main loop (optional)
# If you get these functions to work there should be no hardware

def display(text1,text2):
    oled.fill(0)
    oled.text(text1,0,0)
    oled.text(text2,0,30)
    oled.show() 
    

#================================
stack = []  # For storing position in menu
current =  None  # The b=object currently handling events
menu_data = {} # For getting data out of the menu
task = None   # This holds a task for asyncio


#Little utility function to avoid some module definitions
def set_data(key,value):
    global menu_data
    menu_data[key]=value
#    print ('setting',menu_data)

#This is taken from Peter Hinch's tutorial
def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


#============================
#loop related
    
    
def mainloop():
    "An asynchronous main loop"
    set_global_exception()
    global led

    while True:
        led(not led())
        await step()
        
def run_async(func):
    "run a function asynchronously"
    try:
        asyncio.run(func())
    finally:
        asyncio.new_event_loop()  # Clear retained state
        
def run_menu():
    #convenience function so we dont need module references or global
    run_async(mainloop)

async def step():
    """Poll for scroll and switch events
    """
    button_state = controller.get_state()
    
    if button_state == ControllerState.SELECT:
        current.on_click()
    elif button_state == ControllerState.BACK:
        back()
    elif button_state == ControllerState.SCROLL:
        current.on_scroll(controller.value())
    else: 
        await asyncio.sleep_ms(250)  # determined by trial error - debounces switch
    
    await asyncio.sleep(0)  #play nicely with others
    
#===============================
#Menu navigation related

def back():
    "go back up then menu by excuting this function"
    if len(stack) > 1:
    #the current menu is on the stack so we have to pop it off
        stack.pop()
    #Should be at least one item on stack. Set top of stack to current menu
    set_current( stack.pop())
    
    
def set_current(obj):
    "always do this when we change the control object"
    global current
    stack.append(obj)
    current = obj
    current.on_current()

#=======================
    # Task related

def stop():
    "Convenience function for stopping tasks"
    global task
    """Our routine (neopixels in this case) is stored in a task.
    That allows us to cancel it"""
    try:
        task.cancel()
        task = None
    except:
        pass

 
def make_task(func):
    "convenience function  for starting tasks"
    global task
    task = asyncio.create_task(func())


#=============================
#Object definitions for control objects
  
class Menu():
    "Show a menu on a tiny dispaly by turning a rotatry encoder"
    def __init__(self,menu):
        self.menu = menu
        self.index = 0
        self.increment = 1      
        
    def on_scroll(self,value):
        "Just show the caption"
        self.index = value
        display('', self.menu[value][0])
        
    def on_click(self):
        "Execute the menu item's function"
        (self.menu[self.index][1])()
    
    def on_current(self):
        "Set (and fix if necessary) the index"
        controller.set_value(self.index,0,len(self.menu)-1, swap_direction=True)        
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
        controller.set_value(data_v, swap_direction=False)
        self.value = data_v
        
      
    def on_scroll(self,val):
        "Change the value displayed as we scroll"
        self.value = val
        print("Value: ")
        print(val)
        print("Increment: ")
        print(self.increment)
        display(self.caption,str(val * self.increment))
            
    def on_click(self):
        global menu_data
        "Store the displayed value and go back up the menu"
        menu_data[self.field]= self.value
        back()
        
    def on_current(self):
        "Make sure encode is set properly, set up data and display"
        self.get_initial_value()
        print('get_int',menu_data,self.value, controller.value())
        controller.set_value(self.value,self.low_v,self.high_v,False)
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
        controller.set_value(self.index,0,len(self.choice)-1, swap_direction=True)
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

