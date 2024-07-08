from time import time,sleep
from threading import Thread, Lock
from math import *
import pyautogui as py
import numpy as np
import random
from settings import Settings
import cv2 as cv
from modules.windowcapture import WindowCapture
from scipy.spatial import distance

"""
INITIALIZING: Initialize the bot
SEARCHING: Find the nearby bush to player
MOVING: Move to the selected bush
HIDING: Stop movement and hide in the bush
ATTACKING: Player will attack and activate gadget when enemy is nearby
"""
# Using class as enum
class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    HIDING = 3
    ATTACKING = 4

class Brawlbot:
    player_index = 0
    enemy_index = 2
    results = None
    enemyDistance = None
    lastPlayerCord = None
    
    INITIALIZING_SECONDS = 2
    # input trapezium for the perspective transform 
    TL = [426/1860,159/1046]
    TR = [1434/1860, 159/1046]
    BR = [1521/1860, 1]
    BL = [338/1860, 1]

    def __init__(self,wincap:WindowCapture,speed:float,attack_range:float) -> None:
        self.lock = Lock()
        
        # "brawler" chracteristic
        self.speed = speed
        # short range
        if attack_range >0 and attack_range <=4:
            range_multiplier = 1
            hide_multiplier = 1.3
        # medium range
        elif attack_range > 4 and attack_range <=7:
            range_multiplier = 0.85
            hide_multiplier = 1
        # long range
        elif attack_range > 7:
            range_multiplier = 0.8
            hide_multiplier = 0.8
        
        # attack range in tiles
        self.alert_range = attack_range + 2
        self.attack_range = range_multiplier*attack_range
        self.gadget_range = 0.9*self.attack_range
        self.hide_attack_range = 3.5 # visible to enemy in the bush
        self.HIDINGTIME = hide_multiplier * 23

        self.wincap = wincap
        self.windowWidth, self.windowHeight = wincap.get_dimension()
        self.center_window = wincap.get_window_center()
        self.tilePerWidth = self.windowWidth/27.35
        self.tilePerHeight = self.windowHeight/16.97
        self.perspectiveMatrix = self.find_perspective()

        self.state = BotState.INITIALIZING
        self.timestamp = time()

    def find_perspective(self):
        inputCorners = np.float32([[self.TL[0]*self.windowWidth,self.TL[1]*self.windowHeight], 
                                   [self.TR[0]*self.windowWidth,self.TR[1]*self.windowHeight], 
                                   [self.BR[0]*self.windowWidth,self.BR[1]*self.windowHeight], 
                                   [self.BL[0]*self.windowWidth,self.BL[1]*self.windowHeight]])
        # Calculate the width and height of the new perspective
        outputWidth = round(hypot(inputCorners [0, 0] - inputCorners [1, 0], inputCorners [0, 1] - inputCorners [1, 1]))
        outputHeight = round(hypot(inputCorners [0, 0] - inputCorners [3, 0], inputCorners [0, 1] - inputCorners [3, 1]))
        
        # Set the upper left coordinates for the output rectangle
        x, y = inputCorners[0, 0], inputCorners[0, 1]

        # Specify output coordinates for corners of red quadrilateral in order TL, TR, BR, BL as x, y
        outputCorners = np.float32([[x, y], [x + outputWidth, y], [x + outputWidth, y + outputHeight], [x, y + outputHeight]])

        # Compute the perspective transformation matrix
        matrix = cv.getPerspectiveTransform(inputCorners, outputCorners)
        return matrix
    
    # Function to transform a coordinate from the input plane to the output plane
    def transform_coordinate(self,point):
        pointHomogeneous = np.array([point[0], point[1], 1.0])
        transformedPointHomogeneous = np.dot(self.perspectiveMatrix, pointHomogeneous)
        transformedPointHomogeneous /= transformedPointHomogeneous[2]
        return int(transformedPointHomogeneous[0]), int(transformedPointHomogeneous[1])

    def calculate_tile_distance(self,a,b):
        # normalise the two point by their perspective
        a = self.transform_coordinate(a)
        b = self.transform_coordinate(b)
        differences = np.subtract(a,b)
        tileDiffX = differences[0]/self.tilePerWidth
        tileDiffY = differences[1]/self.tilePerHeight
        return sqrt(tileDiffX**2+tileDiffY**2)

    def ordered_enemy_by_distance(self):
        if self.results:
            # player coordinate
            if self.lastPlayerCord is None:
                playerCord = self.center_window
            else:
                playerCord = self.lastPlayerCord

            def find_distance(position):
                return distance.euclidean(playerCord, position)
            
            enemyCords = self.results[self.enemy_index]
            enemyCords.sort(key=find_distance)
            return enemyCords

    

    def enemy_distance(self):
        """
        Calculate the enemy distance from the player
        """
        if self.results:
            # player coordinate
            if self.lastPlayerCord is None:
                playerCord = self.center_window
            else:
                playerCord = self.lastPlayerCord
            
            # enemy coordinate
            if self.results[self.enemy_index]:
                self.enemyResults = self.ordered_enemy_by_distance()
                if self.enemyResults:
                    self.enemyDistance = self.calculate_tile_distance(playerCord,self.enemyResults[0])
                    
    def update_player_coordinate(self):
        if len(self.results[self.player_index]) == 1:
            self.lastPlayerCord = self.results[self.player_index][0]
        
    # Update object detection results
    def update_results(self,results):
        self.lock.acquire()
        self.results = results
        if self.results:
            self.update_player_coordinate()
        self.lock.release()

    # Starts the thread
    def start(self):
        self.stopped = False
        self.loop_time = time()
        self.count = 0
        t = Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    # Stop the thread
    def stop(self):
        self.stopped = True
        # reset last player position
        self.last_player_pos = None

    # Thread 
    def run(self):
        while not self.stopped:
            sleep(0.01)
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
            elif self.state == BotState.SEARCHING:
                if self.results:
                    self.enemy_distance()