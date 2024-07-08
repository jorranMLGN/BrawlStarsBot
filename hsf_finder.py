from settings import Settings
from modules.windowcapture import WindowCapture
from modules.bot import Brawlbot, BotState
from modules.screendetect import Screendetect, Detectstate
from modules.detection import Detection
from time import sleep
import json
import keyboard

# find brawler height
print("Finding Brawler's HeightScaleFactor: ")
print("Go to the training ground with your selected brawler (brawler menu -> click your brawler -> click the try button -> training ground).")
print("Once you are fully loaded in to the training ground, wait and press the enter key.")
keyboard.wait("enter")
# initialize the WindowCapture class
wincap = WindowCapture(Settings.window_name)
# get window dimension
windowSize = wincap.get_dimension()
# set target window as foreground
sleep(0.5)
wincap.set_window()
# initialize detection class
detector = Detection(windowSize,Settings.model_file_path,Settings.classes)

heightScale = None
while heightScale is None:
    detector.update(wincap.get_screenshot())
    sleep(1)
    heightScale = detector.caculate_heightScale()


print(f"HSF: {round(heightScale,4)}")


brawlerStatsDict = json.load(open("brawler_stats.json"))
brawlerStats = brawlerStatsDict[Settings.brawlerName]
brawlerStats["HSF"] = heightScale
# write to json
with open("brawler_stats.json", "w") as f:
    jsonObject = json.dumps(brawlerStatsDict, indent=4)

    f.write(jsonObject)
print(f"HSF is saved for {Settings.brawlerName}!")