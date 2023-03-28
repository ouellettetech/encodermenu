"""
Demo for the encoder_menu library

This library is for  simple but powerful and intuitive menus
on MCUs running Micropython.

The idea is that various functions can started (or stopped) from a menu.
The example uses some neopixel patterns.

There is also  data entry capacity, integer and strings.

The hardware requirements are basic: a display, a rotary encoder and a switch or button.

"""

from encoder_menu import *
#Good practive says we should import each function but it is a bit verbose
#from encoder_menu import get_integer,info,selection,wizard,wrap_menu,menu_data,dummy,back,run_menu,set_data



#Input buttons controller

class SevenButtonController(Controller):
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

# Display Controller
class LED114Controller(DisplayController):
    def __init__(self):
        self.oled = LCD_1inch14()

    def display(self, menu_lines):
        self.oled.fill(0)
        wri = Writer(self.oled, freesans20)  # verbose = False to suppress console output
        Writer.set_textpos(self.oled, 0, 0)  # In case a previous test has altered this
        for a in menu_lines:
            wri.printstring(a)
            wri.printstring('\n')
        self.oled.show()



# ORDER MATTERS!!
#We have to define things before they can be  used

#Define our default data values first

print("Hello World")
red   =   0x07E0
green =   0x001f
blue  =   0xf800
white =   0xffff
black =   0x0000
yellow =  0xf81f

oled_controller = LED114Controller()
input_controller = SevenButtonController(0)

set_display_controller(oled_controller)
set_input_controller(input_controller)

set_data('hour',12)
set_data('minute',30)
set_data('second',27)
set_data('colour1','GREEN')
set_data('speed',5)
#print (menu_data)

# Now define out data entry and info functions and other action related functions.
#In this example the action functions relate to neopixels.
#and these functions have been declared in their own module for clarity

#define some "get_integer functions for inputing numerical values
#The first example shows the name and order of parameters.
sethours   = get_integer(low_v=1,high_v=24,increment=1,caption='Hours',field='hour')
#Now that we know the order we dont have to repeat the names
setminutes = get_integer( 0, 59 , 1, 'Minute','minute')
setseconds = get_integer(0,59,1,'Second','second')
setyears   = get_integer(1,24,1,'Year','year')
setdays    = get_integer(1,31,1,'Day','day')
setmonths  = get_integer(1,12,1,'Month','month')
brightness = get_integer(0,10,10,'Brightness(%)','brightness')
speed = get_integer(0,20,5,'Speed (0-100)','speed')
hue = get_integer(0,100,1,'Hue (0-100)','hue')

#define some info functions for showing help or status information

colors = ['RED',('Green','GREEN'),'BLUE','YELLOW','ORANGE','PURPLE','WHITE','BLACK']

datetimeinfo = info('Current Datetime\nThis datetime')
setclockinfo   = info('Set up\nTHE CLOCK\nOK')
opendoor= info('Open door\n---------')
closedoor= info('Close door\n.............')
automate= info('Automate door\n#################')

#define a selection

colour1 = selection('colour1',colors)
colour2 = selection('colour2',colors)

# Now that we have our entry functions we can define some wizards

timewizard = wizard([("Hours",sethours),("Minutes",setminutes),("Seconds",setseconds)])
datewizard = wizard([('Years',setyears),("Months",setmonths),("Days",setdays)])

# Now  we have all our action functions  we can define the menus and submenus
# The actual neopixel related functions have been put in the neopixel module


trees     = wrap_menu( [('gum',dummy),('tea-tree',dummy),('red-gum count',dummy),('willow',dummy),('Back!',back)])
patterns  = wrap_menu( [('Chaser',yellow),('Blue',blue),('Rainbow',red),('Back!',back)])
main_menu = wrap_menu( [('Patterns',patterns),('trees',trees),('Brightness',brightness)])
pixels = wrap_menu([('Back!',back)])
settime = wrap_menu( [('Time wizard',timewizard),('Date wizard',datewizard),('Write to clock',setclockinfo),
                      ('Show datetime',datetimeinfo),("Back..",back)])

settings = wrap_menu([('Colour1',colour1),('Colour2',colour2),('Brightness',brightness),('Hue',dummy),('Speed',speed),('Saturation',dummy)])
 
#Root menu should be last menu because it depends on all the previous things
root_menu = wrap_menu([('Set DateTime',settime),('Colour 1',colour1),('Speed',speed),('Patterns',patterns),('Open door',opendoor),
                       ('Close door',closedoor),('Automate door',automate)])

#Finally we set up the root menu and set it running

root_menu()  # Set up the initial root menu by calling its function
run_menu() #Start the main loop running


print('finished -  This should never get here because menu is an endless loop') 




