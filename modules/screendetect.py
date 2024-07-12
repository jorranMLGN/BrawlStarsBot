"""
The screendetect module uses pyautogui to matches pixels' color and take specific action depending on the matches.
e.g. play again button - When play again button is detect by pyautogui.pixelMatchesColor() it will click the play again button.
"""

import pyautogui as py
from threading import Thread, Lock
from time import sleep
from settings import Settings
import turtle
import numpy as np
from PIL import Image
from random import *

"""
IDLE: When state exit,play and load is finished, state is changed to IDLE so
it doesn't spam the terminal with print.

DETECT: Actively check if player is defeated, play again button and loading in.

EXIT: When brawler is defeated, exit the match and stop the bot.

PLAY: When play again is showed, press it and stop the bot.

LOAD: When loading into the match, start the bot

CONNECTION: When the connection is lost

PLAY: When the main menu of brawl stars

PROCEED: When the match is finished, it will click the proceed button

STARDROP: Whenever there is a star drop in the main menu, it will collect the star drop
"""
class Detectstate:
    IDLE = 0
    DETECT = 1
    EXIT = 2
    PLAY_AGAIN = 3
    LOAD = 4
    CONNECTION = 5
    PLAY = 6
    PROCEED = 7
    STARDROP = 8
    
class Screendetect:
    stopped = None
    #RGB value
    defeatedColor = (62,0,0)
    playColor = (224, 186, 8)
    loadColor = (239, 24, 24)
    proceedColor = (35, 115, 255)
    connection_lost_color = (66, 66, 66)
    starDropColor = (222, 72, 227)

    def __init__(self,windowSize,offset) -> None:
        """
        Constructor for the Screendectect class
        """
        self.state = Detectstate.DETECT
        self.lock = Lock()
        self.w = windowSize[0]
        self.h = windowSize[1]
        self.offset_x = offset[0]
        self.offset_y = offset[1]

        # Coordinate
        self.defeated1 = self.round_offset_cord(0.9683,0.1969)
        self.defeated2 = self.round_offset_cord(0.993,0.2046)

        self.starDrop1 = self.round_offset_cord(0.488,0.9303)
        self.starDrop2 = self.round_offset_cord(0.5228,0.9296)
            
        # buttons
        self.playAgainButton = self.round_offset_cord(0.5903,0.9197)
        self.playButton = self.round_offset_cord(0.9419,0.8949)
        self.exitButton = self.round_offset_cord(0.493,0.9187)
        self.loadCord1 = self.round_offset_cord(0.0129,0.0669)
        self.loadCord2 = self.round_offset_cord(0.114,0.0746)
        self.proceedButton = self.round_offset_cord(0.8093,0.9165)

        self.connection_lost_cord = self.round_offset_cord(0.4912,0.5525)
        self.reload_button = self.round_offset_cord(0.2824,0.5812)

    def round_offset_cord(self,x,y):
        return (round(self.w*x)+self.offset_x, round(self.h*y)+self.offset_y)

    def convert_offset_to_normal(self,x,y):
        return  (x-self.offset_x, y-self.offset_y)

    def bgr_to_rgb(self,bgr):
        return (bgr[-1],bgr[1],bgr[0])

    def goto_training(self,delay=1):
        menu = self.round_offset_cord(0.9525,0.0454)
        setting = self.round_offset_cord(0.8676,0.1373)
        editControl = self.round_offset_cord(0.2061,0.3854)
        
        sleep(delay)
        py.click(menu)
        sleep(delay)
        py.click(setting)
        sleep(delay)
        py.click(editControl)

    def exit_training(self):
        exitTraining = self.round_offset_cord(0.5772,0.922)
        back = self.round_offset_cord(0.043,0.043)
        py.click(exitTraining)
        sleep(5)
        py.click(back)
        py.click(back)

    def update_bot_stop(self,bot_stopped):
        self.bot_stopped = bot_stopped
    
    def start(self):
        """
        start screendetect
        """
        self.stopped = False
        t = Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    def stop(self):
        """
        stop screendetect
        """
        self.stopped = True

    # https://stackoverflow.com/a/66405993
    def display_detect_pixel(self):
        def setwindowsize(x=640, y=640):
            turtle.setup(x, y)
            turtle.setworldcoordinates(0,0,x,y)
            turtle.bgcolor(0,0,0)

        def drawpixel(cord,color,pixelsize=1):
            x,y = cord 
            turtle.tracer(0, 0)
            turtle.colormode(255)
            turtle.penup()
            turtle.setpos(x*pixelsize,y*pixelsize)
            turtle.color(color)
            turtle.pendown()
            turtle.begin_fill()
            for i in range(4):
                turtle.forward(pixelsize)
                turtle.right(90)
            turtle.end_fill()

        def showimage():
            turtle.hideturtle()
            turtle.update()

        setwindowsize(self.w,self.h)
        drawpixel(self.convert_offset_to_normal(self.loadCord1[0], self.loadCord1[1]),self.bgr_to_rgb(self.loadColor))
        drawpixel(self.convert_offset_to_normal(self.playAgainButton[0], self.playAgainButton[1]),self.bgr_to_rgb(self.playColor))
        drawpixel(self.convert_offset_to_normal(self.defeated1[0], self.defeated1[1]),self.bgr_to_rgb(self.defeatedColor))
        drawpixel(self.convert_offset_to_normal(self.defeated2[0], self.defeated2[1]),self.bgr_to_rgb(self.defeatedColor))
        drawpixel(self.convert_offset_to_normal(self.starDrop1[0], self.starDrop1[1]),self.bgr_to_rgb(self.starDropColor))
        drawpixel(self.convert_offset_to_normal(self.starDrop2[0], self.starDrop2[1]),self.bgr_to_rgb(self.starDropColor))
        drawpixel(self.convert_offset_to_normal(self.playButton[0], self.playButton[1]),self.bgr_to_rgb(self.playColor))
        drawpixel(self.convert_offset_to_normal(self.proceedButton[0], self.proceedButton[1]),self.bgr_to_rgb(self.proceedColor))
        showimage()             

    def is_load_in(self):
        return (py.pixelMatchesColor(self.loadCord1[0], self.loadCord1[1],self.loadColor,tolerance=30) or 
                    py.pixelMatchesColor(self.loadCord2[0], self.loadCord2[1],self.loadColor,tolerance=30))

    def is_play_again_button(self):
        return py.pixelMatchesColor(self.playAgainButton[0], self.playAgainButton[1],self.playColor,tolerance=15)

    def is_exit(self):
        return (py.pixelMatchesColor(self.defeated1[0], self.defeated1[1],
                                                     self.defeatedColor,tolerance=15)
                        or py.pixelMatchesColor(self.defeated2[0], self.defeated2[1],
                                                     self.defeatedColor,tolerance=15)) and not(self.bot_stopped)
    def is_star_drop(self):
        return (py.pixelMatchesColor(self.starDrop1[0], self.starDrop1[1], self.starDropColor,tolerance=15)
                    or py.pixelMatchesColor(self.starDrop2[0], self.starDrop2[1], self.starDropColor,tolerance=15))
    def is_play_button(self):
        return py.pixelMatchesColor(self.playButton[0], self.playButton[1], self.playColor, tolerance=15)
    
    def is_proceed_button(self):
        return py.pixelMatchesColor(self.proceedButton[0], self.proceedButton[1], self.proceedColor, tolerance=25)
    
    def run(self):
        while not self.stopped:
            sleep(0.01)
            if self.state == Detectstate.IDLE:
                sleep(3)
                self.state = Detectstate.DETECT
            
            elif self.state == Detectstate.DETECT:
                try:
                    if self.is_play_again_button():
                        print("Playing again")
                        self.lock.acquire()
                        self.state = Detectstate.PLAY_AGAIN
                        self.lock.release()
                    
                    elif py.pixelMatchesColor(self.loadCord1[0], self.loadCord1[1],self.loadColor,tolerance=30):
                        print("Loading in")
                        self.lock.acquire()
                        sleep(6)
                        self.state = Detectstate.LOAD
                        self.lock.release()
                    
                    elif self.is_exit():
                        print("Exiting match")
                        self.lock.acquire()
                        self.state = Detectstate.EXIT
                        self.lock.release()
                    
                    # elif pyautogui.pixelMatchesColor(self.connection_lost_cord[0],self.connection_lost_cord[1],self.connection_lost_color,tolerance=1):
                    #     print("Connection Lost")
                    #     self.lock.acquire()
                    #     self.state = Detectstate.CONNECTION
                    #     self.lock.release()
                    
                    elif self.is_star_drop():
                        print("Collecting Star Drop")
                        self.lock.acquire()
                        self.state = Detectstate.STARDROP
                        self.lock.release()
                        
                    elif self.is_play_button():
                        print("Play")
                        self.lock.acquire()
                        self.state = Detectstate.PLAY
                        self.lock.release()

                    elif self.is_proceed_button():
                        print("Proceed")
                        self.lock.acquire()
                        self.state = Detectstate.PROCEED
                        self.lock.release()
                
                except OSError:
                    pass
                        
            elif self.state == Detectstate.PLAY_AGAIN:
                # click the play button
                sleep(0.05)
                py.click(x=self.playAgainButton[0], y=self.playAgainButton[1], button="left")
                sleep(0.05)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.LOAD:
                sleep(0.1)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.EXIT:
                # release movement key
                py.mouseUp(button = Settings.movement_key)
                sleep(5)
                # click the exit button
                py.click(x=self.exitButton[0], y=self.exitButton[1], button="left")
                sleep(0.05)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.CONNECTION:
                sleep(20)
                py.click(x=self.reload_button[0], y=self.reload_button[1], button="left")
                sleep(0.05)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.PLAY:
                # click the play button
                sleep(0.05)
                py.click(x=self.playButton[0], y=self.playButton[1], button="left")
                sleep(0.05)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.PROCEED:
                sleep(0.5)
                py.click(x=self.proceedButton[0], y=self.proceedButton[1], button="left", clicks=2)
                sleep(0.5)
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()
            
            elif self.state == Detectstate.STARDROP:
                py.press("e",presses=5)
                sleep(6)
                py.press("e")
                self.lock.acquire()
                self.state = Detectstate.IDLE
                self.lock.release()