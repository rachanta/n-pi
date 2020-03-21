# Author: Iqbal Mohomed
# Notice: This code is provided as is - no warranties
#
# For details on the project, see my personal blog: slowping.com
# This is a personal project done on my own time. 
#
# 
# Python version: 2.6
# Libraries used: pyBrain, nxt-python (v2.2.1), PIL (Python Image Libary)
#
# This code has been used successfully on Windows 7. 
# On Mac OS X (Snow Leopard), the SynchronizedMotors class has given me some grief.
#
# Initially, I've placed all my code into this file. I hope to clean it up as I get time.
#
# Have fun!!

import nxt
import sys
import time
import tty, termios
from PIL import Image
import urllib
import pickle
import numpy as np
from time import sleep

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer



net = buildNetwork(10800,64,3,bias=True)
ds = SupervisedDataSet(10800,3)
f = open('/home/pi/0nxt/neurobot/training.txt','r')
st=f.readlines()
print len(st)



def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch




def save_net(nnet,fname):
	fileOb = open(fname,'w')
	pickle.dump(nnet, fileOb)
	fileOb.close()

def load_net(fname):
	fileOb = open(fname,'r');
	nnet = pickle.load(fileOb);
	fileOb.close();
	nnet.sorted = False
	nnet.sortModules()
	return nnet;

def use_nnet(nnet,im):
	cmd = ''
	lst = list(im.getdata())
	res=nnet.activate(lst)
	val = res.argmax()
	if val == 0:
		cmd = 'f'
	elif val == 1:
		cmd = 'l'
	elif val == 2:
		cmd = 'r'		
	return cmd

def exec_cmd(cmd):
    if cmd == 'f':
        inchforward()
    elif cmd == 'l':
        halfleft()
    elif cmd == 'r':
        halfright()
    elif cmd == 'x':
        brick.sock.close()

def auto(nnet):
	while True:
            im=take_pic()
	    cmd=use_nnet(nnet,im)
	    exec_cmd(cmd)
	    print "executing .." + cmd
	    time.sleep(3)

def initBrick():
	global brick
	global left
	global right
	global centre
	global both
	global rightboth
	global leftboth

        brick = nxt.locator.find_one_brick()
        left = nxt.Motor(brick, nxt.PORT_B)
        right = nxt.Motor(brick, nxt.PORT_C)
        #centre = nxt.Motor(brick, PORT_A)
        both = nxt.SynchronizedMotors(right, left, 0)
        rightboth = nxt.SynchronizedMotors(left, right, 100)
        leftboth = nxt.SynchronizedMotors(right, left, 100)


def train(net,ds,p=800):
	trainer = BackpropTrainer(net,ds)
	trainer.trainUntilConvergence(maxEpochs=p)
	return trainer


def makeds(st,ds):
	i=0
	L = len(st)
	while i < L:
		inp = map(int,st[i].split()[0:-3])
		ou = map(int,st[i].split()[-3:])
		ds.addSample(inp,ou)
		i+=1



def take_pic():
	res=urllib.urlretrieve('http://192.168.43.1:8080/shot.jpg')
	im = Image.open(res[0])
	nim = im.convert('L')
	nim2=nim.resize((120,90))
	return nim2;

def trainer():
    while True:
        im=take_pic() # download pic and read it to a file
        cmd = accept_execute_cmd()
        record_data(im,cmd) #photo and cmd

def cmd2arr(cmd):
	res = [0] * 3;
	if cmd == 'f':
		res[0] = 1;
	elif cmd == 'l':
		res[1] = 1;
	elif cmd == 'r':
		res[2] = 1;
	return res;


def makestr(lst):
	res = ""
	for i in lst:
		res += str(i) + " "
	return res;

def record_data(im,cmd):
	# read photo.jpg and make it into array
	lst = list(im.getdata())
	cmdarr = cmd2arr(cmd)
	lst.extend(cmdarr)
	f = open('training.txt','a')
	st=makestr(lst)
	f.write(st + '\r\n')
	f.close()


	
def leftturn():
        print "Left Turn"
        leftboth.turn(90, 120, False)
        sleep(2)

def halfleft():
        print "Half Left Turn"
        leftboth.turn(90, 45, False)
        sleep(2)


def rightturn():
        print "Right Turn"
        rightboth.turn(90, 120, False)
        sleep(2)

        
def halfright():
        print "Half Right Turn"
        rightboth.turn(90, 45, False)
        sleep(2)
        
def aboutturn():
        print "About Right Turn"
        rightboth.turn(90, 480, False)

def inchforward():   
    print "Inch Forward"   
    both.turn(70, 360, False)
    sleep(2)
    
def inchreverse():
    print "Inch Reverse" 
    both.turn(-70, 360, False)
   

def accept_execute_cmd():
    cmd = ''
    gotCmd = False
    print "CMD: "
    while gotCmd == False :
        cmd = getch()
        if cmd == 'f' or cmd == 'l' or cmd == 'r' :
            exec_cmd(cmd)
            gotCmd = True
        elif cmd == 'x':
            brick.sock.close()
            gotCmd = False
            exit()
    print cmd + "\n"
    return cmd
    

###############################################################
# The following sections are meant to be exclusive. 
# Comment one of the sections to acheive your desired function.
###############################################################

# To get Training samples, uncomment below
print "Loaded"
#initBrick()
#trainer()


# To train neuralnet, uncomment below
#makeds(st,ds)
#train(net,ds,800)
#save_net(net,'/home/pi/0nxt/neurobot/neuronet_15_1000.dat')


# For self-drive, uncomment below
#initBrick()
#auto(net)

