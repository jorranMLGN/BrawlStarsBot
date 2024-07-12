from time import time,sleep
from threading import Thread, Lock
from math import *
import pyautogui as py
import numpy as np
from settings import Settings
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
    bush_index = 1
    enemy_index = 2
    results = None
    enemyDistance = None
    lastPlayerCord = None
    INITIALIZING_SECONDS = 2

    def __init__(self,wincap:WindowCapture,speed:float,attack_range:float) -> None:
        self.lock = Lock()
        
        # "brawler" chracteristic
        self.speed = speed
        # short range
        if attack_range > 0 and attack_range <=4:
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
        self.brawlerCenter = wincap.get_brawler_center()

        self.state = BotState.INITIALIZING
        self.timestamp = time()

    def calculate_tile_xy(self,a,b):
        # normalise the two point by their perspective
        a = self.wincap.transform_coordinate(a)
        b = self.wincap.transform_coordinate(b)
        differences = np.subtract(b,a)
        tileDiffX = differences[0]/self.wincap.tilePerWidth
        tileDiffY = differences[1]/self.wincap.tilePerHeight
        return (tileDiffX,tileDiffY)
    
    def calculate_tile_distance(self,a,b):
        tileDiffX, tileDiffY = self.calculate_tile_xy(a,b)
        return sqrt(tileDiffX**2+tileDiffY**2)
    
    def get_player_cord(self):
        # player coordinate
        if self.lastPlayerCord is None:
            playerCord = self.brawlerCenter
        else:
            playerCord = self.lastPlayerCord

        return playerCord
    
    def ordered_enemy_by_distance(self):
        if self.results:
            playerCord = self.get_player_cord()
            def find_distance(position):
                return distance.euclidean(playerCord, position)
            
            enemyCords = self.results[self.enemy_index]
            enemyCords.sort(key=find_distance)
            return enemyCords
    
    def calculate_bushes_tiles(self):
        if self.results:
            if self.results[self.bush_index]:
                playerCord = self.get_player_cord()
                return [round(self.calculate_tile_xy(playerCord,bushPosition)) for bushPosition in self.results[self.bush_index]]

    def enemy_distance(self):
        """
        Calculate the enemy distance from the player
        """
        if self.results:
            playerCord = self.get_player_cord()
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
            sleep(1)
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
            elif self.state == BotState.SEARCHING:
                if self.results:
                    bushTiles = self.calculate_bushes_tiles()
                    if len(bushTiles) == 1:
                        print(bushTiles)