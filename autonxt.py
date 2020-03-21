import os
import re
import Tkinter
import nxt
import sys
import nxt.locator
import cv2
import urllib2
import numpy as np
import sys
import webbrowser
from selenium import webdriver
from time import sleep
from functools import partial
from nxt.sensor import *
from nxt.motor import *
from multiprocessing import Process

brick = nxt.locator.find_one_brick()
left = nxt.Motor(brick, PORT_B)
right = nxt.Motor(brick, PORT_C)
centre = nxt.Motor(brick, PORT_A)
both = nxt.SynchronizedMotors(left, right, 0)
rightboth = nxt.SynchronizedMotors(left, right, 100)
leftboth = nxt.SynchronizedMotors(right, left, 100)


class NxtSensor():
        r'''A high-level controller for the Ra Sensor model.
        
            This class implements methods for the most obvious actions performable
            by Ra Sensor, such as walk, wave its arms, and retrieve sensor samples.
            Additionally, it also allows direct access to the robot's components
            through public attributes.
        '''
        def __init__(self, brick):
            r'''Creates a new Ra Sensor controller.
            
                brick
                    Either an nxt.brick.Brick object, or an NXT brick's name as a
                    string. If omitted, a Brick named 'NXT' is looked up.
            '''
            self.brick = brick
            self.touch = Touch(brick, PORT_1)
            self.sound = Sound(brick, PORT_2)
            self.light = Light(brick, PORT_3)
            self.ultrasonic = Ultrasonic(brick, PORT_4)

        def echolocate(self):
            r'''Reads the Ultrasonic sensor's output.
            '''
            return self.ultrasonic.get_sample()
        
        def feel(self):
            r'''Reads the Touch sensor's output.
            '''
            return self.touch.get_sample()

        def hear(self):
            r'''Reads the Sound sensor's output.
            '''
            return self.sound.get_sample()

        def say(self, line, times=1):
            r'''Plays a sound file named (line + '.rso'), which is expected to be
                stored in the brick. The file is played (times) times.

                line
                    The name of a sound file stored in the brick.

                times
                    How many times the sound file will be played before this method
                    returns.
            '''
            for i in range(0, times):
                self.brick.play_sound_file(False, line + '.rso')
                sleep(1)

        def see(self):
            r'''Reads the Light sensor's output.
            '''
            return self.light.get_sample()

    
sense = NxtSensor(brick)         

    


def distleft():
    nxt.Motor.reset_position(centre, True)
    tachostatus =  str(nxt.Motor.get_tacho(centre))
    tachostatus1 = re.sub('[(),]', '', tachostatus)
    print tachostatus1
    arraytacho = np.fromstring(tachostatus1, dtype=int, sep=' ')
    counttacho = arraytacho[0]
    print counttacho

    centre.turn(10, 90, True)
    global leftdist
    leftdist = sense.echolocate()
    print leftdist
    
    tachostatusnext =  str(nxt.Motor.get_tacho(centre))
    tachostatusnext1 = re.sub('[(),]', '', tachostatusnext)
    print tachostatusnext1
    arraytachonext = np.fromstring(tachostatusnext1, dtype=int, sep=' ')
    counttachonext = arraytachonext[0]
    print counttachonext

    counttachodiff = abs(counttachonext - counttacho)
    print counttachodiff

    centre.turn(-10, counttachodiff, True)
    nxt.Motor.reset_position(centre, True)
    

def distright():
    nxt.Motor.reset_position(centre, True)
    tachostatus2 =  str(nxt.Motor.get_tacho(centre))
    tachostatus3 = re.sub('[(),]', '', tachostatus2)
    print tachostatus3
    arraytacho1 = np.fromstring(tachostatus3, dtype=int, sep=' ')
    counttacho1 = arraytacho1[0]
    print counttacho1

    centre.turn(-10, 90, True)
    global rightdist
    rightdist = sense.echolocate()
    print rightdist
    
    tachostatusnext2 =  str(nxt.Motor.get_tacho(centre))
    tachostatusnext3 = re.sub('[(),]', '', tachostatusnext2)
    print tachostatusnext3
    arraytachonext1 = np.fromstring(tachostatusnext3, dtype=int, sep=' ')
    counttachonext1 = arraytachonext1[0]
    print counttachonext1

    counttachodiff1 = abs(counttachonext1 - counttacho1)
    print counttachodiff1

    centre.turn(10, counttachodiff1, True)
    nxt.Motor.reset_position(centre, True)    




def applybrake():
    both.brake()

def beep_short():
    brick.play_tone_and_wait(500, 100)

def beep_long():
    brick.play_tone_and_wait(500, 700)
 

def beep_extralong():
    brick.play_tone_and_wait(500, 2000)


def leftturn():
    print "Left Turn"
    leftboth.turn(90, 90, False)

def rightturn():
    print "Right Turn"
    rightboth.turn(90, 90, False)

def inchforward():   
    print "Inch Forward"   
    both.turn(70, 360, False)

    
def inchreverse():
    print "Inch Reverse" 
    both.turn(-70, 360, False)
    sleep(2)

def stop():   
    rcp.poll = False
    applybrake()
    print "Stopped"


def autorun():
    if rcp.poll:
            if (sense.feel() == 0) :
                    if sense.hear() < 950 :
                        if sense.echolocate() > 60 :
                            print "Forward"
                            both.run(127) 
                            rcp.after(1000, autorun)         
                        else :
                            print "Obstruction, taking evasive action"    
                            stop()
                            rcp.poll = True
                            distleft()
                            distright()
                            if leftdist > rightdist :
                                leftturn()
                                autorun()
                            elif rightdist >= leftdist :
                                rightturn()
                                autorun()
                    else :
                        applybrake()                              
            else :  
                stop()
                rcp.quit()




def CaptureRobotPerspectiveWan() :
        if rpv.poll :
	        #chrome_path='/usr/lib/chromium-browser/chromium-browser'
                #webbrowser.get(chrome_path).open('http://alfred.computer')
                print "Open Chromium Browser to go to http://alfred.computer"
                print "to see Robot Perspective over WAN"

 
def CaptureRobotPerspectiveLan() :
	if rpv.poll :
		host = "192.168.43.1:8080"
		if len(sys.argv)>1:
    			host = sys.argv[1]
		hoststr = 'http://' + host + '/video'
		print 'Streaming ' + hoststr
 
		stream=urllib2.urlopen(hoststr)
 
		bytes=''
		while True:
	    		bytes+=stream.read(1024)
	    		a = bytes.find('\xff\xd8')
	    		b = bytes.find('\xff\xd9')
	    		if a!=-1 and b!=-1:
	        		jpg = bytes[a:b+2]
	        		bytes= bytes[b+2:]
	        		i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
	        		cv2.imshow(hoststr,i)
    				if cv2.waitKey(1) & 0xFF == ord('q'):
        				break # Press Q to close the frame <-- how to close frame
		# When everything done, release the capture		
		cv2.destroyAllWindows()	
		



class VisionControlPad(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        btn_list = ['Robot LAN View', 'Robot WAN View', 'Quit Capture']
        self.grid()
        lf = Tkinter.LabelFrame(text="ratech-vision-control", bd=3)
        lf.pack(padx=15, pady=10)

        r = 1
        c = 0
        n = 0
        btn = list(range(len(btn_list)))
        for label in btn_list:
            cmd = partial(self.click, label)
            btn[n] = Tkinter.Button(lf, text=label, width=30, command=cmd)
            btn[n].grid(row=r, column=c)
            n += 1
            c += 1
            if c > 0:
                c = 0
                r += 1


	
    def click(self,btn):         
        if (btn == 'Robot LAN View'):
		rpv.after(1000, CaptureRobotPerspectiveLan)
        if (btn == 'Robot WAN View'):
		rpv.after(1000, CaptureRobotPerspectiveWan)
        elif (btn == 'Quit Capture'):
                rpv.destroy()
		exit(0)	    




class OnScreenKeyboard(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        btn_list = ['Auto Run', 'Stop', 'Quit', 'Beep',
                    'Inch Forward', 'Inch Reverse', 'Left Turn', 'Right Turn']
                   
        self.grid()
        lf = Tkinter.LabelFrame(text="ratech_motion_control", bd=3)
        lf.pack(padx=15, pady=10)

        r = 1
        c = 0
        n = 0
        btn = list(range(len(btn_list)))
        for label in btn_list:
            cmd = partial(self.click, label)
            btn[n] = Tkinter.Button(lf, text=label, width=18, command=cmd)
            btn[n].grid(row=r, column=c)
            n += 1
            c += 1
            if c > 3:
                c = 0
                r += 1
	
    def click(self,btn):         
        if (btn == 'Auto Run'):
            rcp.poll = True   
            beep_long()   
            autorun()
        elif (btn == 'Inch Forward'):
            beep_short()   
            inchforward()
        elif (btn == 'Inch Reverse'):
            beep_short()   
            inchreverse()
        elif (btn == 'Left Turn'):		
            leftturn()
        elif (btn == 'Right Turn'):
            rightturn()
        elif (btn == 'Beep'):		
            beep_long()
        elif (btn == 'Stop'):		
            stop()
        elif (btn == 'Quit'):
            stop()
            rcp.destroy()
            exit(0)
       
 
def loop_a():
    global rpv
    rpv = VisionControlPad(None)

    w = 320 # width for the Tk root
    h = 120 # height for the Tk root
    x = 160
    y = 540

    rpv.poll = True
    rpv.title('NXT View Control')
    rpv.geometry('%dx%d+%d+%d' % (w, h, x, y))
    rpv.mainloop() 


def loop_b():
    global rcp   
    rcp = OnScreenKeyboard(None)

    w = 720 # width for the Tk root
    h = 100 # height for the Tk root
    x = 500
    y = 540

    rcp.poll = True
    rcp.title('NXT Remote')
    rcp.geometry('%dx%d+%d+%d' % (w, h, x, y))
    rcp.mainloop()




if __name__ == '__main__' :
    #loop_a.daemon = True
    #loop_b.daemon = True
    Process(target=loop_a).start()
    Process(target=loop_b).start()
  
