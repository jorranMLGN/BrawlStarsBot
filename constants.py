import json
from modules.print import bcolors
brawler_stats_dict = json.load(open("brawler_stats.json"))

class Constants:
    #! change the brawler name, if its not found please manually change the stats it below
    brawler_name = "shelly"
    
    #! Change the speed and range for the brawler you are using
    """
    go to https://pixelcrux.com/Brawl_Stars/Brawlers/
    to find brawler's speed and attack range
    and use hsf_finder.py to get the brawler's height scale factor
    eg. eve's speed (2.4), attack_range (9.33) and
    height scale factor (0.158)
    """
    speed = 2.57 # units: (tiles per second)
    attack_range = 7.67 # units: (tiles per second)
    heightScaleFactor = 0.154
    
    #! Change this to suit the current map
    # map's characteristic
    # if map have a lot of walls make sharpCorner True otherwise False
    sharpCorner = False
    # if brawler spawn in the middle of the map make centerOrder False otherwise True
    centerOrder = True
    """
    If you have multiple instance of bluestacks or you got
    "Bluestacks App Player not found". Please change the window
    name to name located on the top left corner of your bluestacks
    eg. Bluestacks App Player 1, Bluestacks App Player 2, etc
    """
    window_name = "Bluestacks App Player 1"
    # Make this False if detection_test is outputing a blank screen, otherwise True.
    focused_window = False

    #! Change this to True if you have Nvidia graphics card and CUDA installed
    nvidia_gpu = False
    
    #! Do not change these
    # Main contants
    DEBUG = True
    # Detector constants
    classes = ["Player","Bush","Enemy","Cubebox"]
    """
    Threshold's index correspond with classes's index.
    e.g. First element of classes is player so the first
    element of threshold is threshold for player.
    """
    threshold = [0.35,0.45,0.55,0.65]

    try:
        brawler_stats = brawler_stats_dict[brawler_name.lower().strip()]
        display_str = f"Using {brawler_name.upper()}'s stats if the selected brawler is not {brawler_name.upper()}, \nplease manually modify at constants.py."
        standard_hsf = 0.15
        if len(brawler_stats) == 2:
            brawler_stats.append(standard_hsf)
        elif len(brawler_stats) > 3:
            display_str = "brawler stats has more then 3 element, using stats at constants.py"
            brawler_stats = 3*[None]
    except KeyError:
        brawler_stats = 3*[None]
        display_str = f"{brawler_name.upper()}'s stats is not found in the JSON. Using speed, attack range and height scale factor in constant.py, please manually modify at constants.py if you havent."
    print("")
    print(bcolors.WARNING + display_str +bcolors.ENDC)
    speed = brawler_stats[0] or speed # units: (tiles per second)
    attack_range = brawler_stats[1] or attack_range # units: (tiles per second)
    heightScaleFactor = brawler_stats[2] or heightScaleFactor

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
    midpoint_offset = 12
    
    float_int_dict = {
        "speed":speed,
        "attack_range":attack_range,
        "heightScaleFactor": heightScaleFactor
    }

    bool_dict = {
        "sharpCorner": sharpCorner,
        "centerOrder": centerOrder,
        "nvidia_gpu": nvidia_gpu
    }

    for key in float_int_dict:
        assert type(float_int_dict[key]) == float or type(float_int_dict[key]) == int, f"{key.upper()} should be a integer or a float"

    for key in bool_dict:
        assert type(bool_dict[key]) == bool,f"{key.upper()} should be True or False"

if __name__ == "__main__":
    pass