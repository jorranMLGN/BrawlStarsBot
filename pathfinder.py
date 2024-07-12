from PIL import Image
import math
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Pathfinder:
    canWalkOnWater = False
    xViewTileRange = 24
    yViewTileRange = 18 # tiles

    # rgb
    empty = (255,255,255) # white
    walls = (0,0,0) # black
    bush = (0,255,0) # green
    spawn = (255,0,0) # red
    water = (0,0,255) # blue
    cubebox = (255,255,0) # yellow

    walkable = [empty,bush,spawn]
    unwalkable = [walls,cubebox]

    if canWalkOnWater:
        walkable.append(water)
    else:
        unwalkable.append(water)

    def __init__(self,mapImgPath) -> None:
        # Read an Image
        self.img = Image.open(mapImgPath)
        self.width, self.height = self.img.size
        self.matrix = self.find_walkable_matrix()
        self.angles, self.spawnPoints = self.find_spawnpoint_angles()

        self.grid = Grid(matrix=self.matrix)
        self.finder = AStarFinder()

    def find_walkable_matrix(self):
        # find walkable matrix
        walkableMatrix = []
        for x in range(0, self.width):
            temp = []
            for y in range(0, self.height):
                r, g, b, _= self.img.getpixel((x,y))
                if (r,g,b) in self.walkable:
                    temp.append(1)
                elif (r,g,b) in self.unwalkable:
                    temp.append(0)
            walkableMatrix.append(temp)
        return walkableMatrix

    def find_spawnpoints(self):
        # find spawn point
        spawnPoints = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                r, g, b, _= self.img.getpixel((x,y))
                if (r,g,b) == self.spawn:
                    spawnPoints.append((x,y))
        return spawnPoints

    def find_angle(self,start:tuple,end:tuple):
        deltaX = end[0] - start[0] # x2 - x1
        deltaY = end[1] - start[1] # y2 - y1

        try:
            theta = math.degrees(math.atan(deltaY/deltaX)) # gradient = tan(theta)
        except ZeroDivisionError:
            if deltaX == 0:
                if deltaY == 0:
                    return
                elif deltaY > 0:
                    theta = 270
                elif deltaY < 0:
                    theta = 90
        
            if deltaX == 0:
                if deltaX == 0:
                    return
                elif deltaX > 0:
                    theta = 360
                elif deltaY < 0:
                    theta = 180   
            return theta

        # quadrant one on the x-y axis
        if deltaX > 0 and deltaY < 0:
            theta = - theta
        # quadrant two 
        elif deltaX < 0 and deltaY < 0 :
            theta = 180 - theta
        # quadrant three
        elif deltaX < 0 and deltaY > 0:
            theta = 180 - theta
        # quadrant four
        elif deltaX > 0  and deltaY > 0:
            theta = 360 - theta
        
        return round(theta,2)
    
    def find_spawnpoint_angles(self):
        spawnPoints = self.find_spawnpoints()
        # angle of spawn point to the center of the map
        centerPoint = (self.width//2, self.height//2)
        angles = [self.find_angle(centerPoint,spawnPoint) for spawnPoint in spawnPoints]

        # sort the list into ascending order
        angles, spawnPoints = (list(t) for t in zip(*sorted(zip(angles, spawnPoints))))

        return (angles, spawnPoints)

    def display_walkable_matrix(self):
        # illustrate walkableMatrix in a black and white image
        im = Image.new(mode="RGB", size=(self.width, self.height))
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.matrix[x][y] == 1:
                    im.putpixel((x,y), (255,255,255))
                else:
                    im.putpixel((x,y), (0,0,0))
        im.show()

    def find_path(self,start,end):
        
        start = self.grid.node(start[1],start[0])
        end = self.grid.node(end[1],end[0])

        # self.grid.cleanup()
        path, runs = self.finder.find_path(start, end, self.grid)

        return path
        
pathfinder = Pathfinder('skull_creek.png')
