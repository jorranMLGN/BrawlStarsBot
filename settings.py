import json
from modules.print import bcolors
brawlerStatsDict = json.load(open("brawler_stats.json"))

class Settings:
    #! Brawler's stats
    """
    change the brawler_name to the one you are using,
    follows https://pixelcrux.com/Brawl_Stars/Brawlers/# naming convention
    e.g "8-bit" or "Larry & Lawrie"
    """
    
    brawlerName = "Bibi"
    
    #! Map's characteristics
    """
    Change this to suit the current map
    If the map have a lots of walls make sharpCorner True otherwise make it False
    If the brawler spawn in the middle of the map make centerOrder False otherwise make it True
    """
    sharpCorner = True
    centerOrder = True
    
    #! Window Capture
    """
    If you have multiple instance of bluestacks or you got
    "Bluestacks App Player not found". Please change the window
    name to name located on the top left corner of your bluestacks
    eg. Bluestacks App Player 1, Bluestacks App Player 2, etc
    """
    window_name = "Bluestacks App Player"
    # Make this False if detection_test is outputting a blank screen, otherwise True.
    focused_window = True

    #! Change this to True if you have Nvidia graphics card and CUDA installed
    nvidia_gpu = None

    # Main contants
    """
    Generate a second window with detection annotated
    """
    DEBUG = True

    #! Do not change these
    # Detector constants
    classes = ["Player","Bush","Enemy","Cubebox"]
    """
    Threshold's index correspond with classes's index.
    e.g. First element of classes is player so the first
    element of threshold is threshold for player.
    """
    threshold = [0.4,0.4,0.43,0.65]

    print("")
    print(bcolors.BOLD + bcolors.OKGREEN + "Check https://github.com/Jooi025/BrawlStarsBot for the latest update!" + bcolors.ENDC)
    print("")

    # find brawler in the json 
    try:
        brawlerStats = brawlerStatsDict[brawlerName]
        invalidBrawlerString = f"Selected Brawler: {brawlerName}"
    except KeyError:
        invalidBrawlerString = f"Invalid Brawler name in settings.py! (Case Sensitive)\nYou mean this?\n"
        brawlersNameList = [key for key in brawlerStatsDict]
        for name in brawlersNameList:
            if name[0].lower() == brawlerName[0].lower():
                invalidBrawlerString += f"- {name}\n"
        print(bcolors.WARNING + invalidBrawlerString + bcolors.ENDC)
        exit()

    movementSpeed = brawlerStats["Base"]["Movement speed"]
    attackRange = brawlerStats["Attack"]["Range"]
    
    try:
        heightScale = brawlerStats["HSF"]
    except KeyError:
        heightScale = None
        print(bcolors.FAIL + "HSF not found, run \"hsf_finder.py\" for more info!" + bcolors.ENDC)

    print(bcolors.OKBLUE + f"Speed: {movementSpeed} tiles/second \nAttack Range: {attackRange} tiles\nHSF: {heightScale}\n" + bcolors.ENDC)

    # interface
    if nvidia_gpu is None:
        # load TensorRT interface
        model_file_path = "yolov8_model/yolov8.engine"
        half = False
        imgsz = 640
    elif nvidia_gpu:
        # load pytorch interface
        model_file_path = "yolov8_model/yolov8.pt"
        half = False
        imgsz = (384,640)
    else:
        # load openvino interface
        model_file_path = "yolov8_model/yolov8_openvino_model"
        half = True
        imgsz = (384,640)
    
    #bot constant
    movement_key = "middle"
    midpointOffsetScale = 0.024
    
    bool_dict = {
        "sharpCorner": sharpCorner,
        "centerOrder": centerOrder,
    }

    for key in bool_dict:
        assert type(bool_dict[key]) == bool,f"{key.upper()} should be True or False"

if __name__ == "__main__":
    pass