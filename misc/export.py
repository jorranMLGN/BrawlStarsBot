from ultralytics import YOLO

# Load a model
model = YOLO("yolov8_model\\yolov8.pt")  # load a custom trained model

# Export the model
model.export(format="engine",imgsz=640)