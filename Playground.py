#TRAINING
"""from ultralytics import YOLO

model = YOLO("yolov8m.yaml")

result = model.train(data='data.yaml', epochs = 1, imgsz = 640) #device = 0 DOES NOT WORK

#30 mins for 1 epoch"""

from ultralytics import YOLO

model = YOLO('custom_model.pt') #Change to custom model

#source = 0 means using the camera
results = model.track(source = "sample_vids/sample_vid.mp4", save = True, show=True, tracker='bytetrack.yaml')


"""import cv2
#Use ultralytics solutions instead of roboflow supervision - MAY CHANGE
from ultralytics import YOLO, solutions
from ultralytics.utils.plotting import Annotator, colors 

model = YOLO("Models/custom_model_v2.pt")
cap = cv2.VideoCapture("sample_vids/sample_vid.mp4") #change to 0 for ReDragon
cap2 = cv2.VideoCapture("sample_vids/sample_vid_2.mp4") #change to something else for Coral Cam

names = model.names
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
# Blur ratio
blur_ratio = 50 #For Blurring

# Define line points
line_points = [(350, 400), (550, 375)] #For Counting

#Initialization of Object Counter
counter = solutions.ObjectCounter(
    view_img=False,
    reg_pts=line_points,
    names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

# Video writer
video_writer = cv2.VideoWriter("preliminary_work.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    #OBJECT BLURRING CODE ------------------------------------------------------
    #results = model.predict(im0, show=False)
    results = model.track(im0, persist=True, show=False, tracker="bytetrack.yaml")
    boxes = results[0].boxes.xyxy.cpu().tolist()
    clss = results[0].boxes.cls.cpu().tolist()
    annotator = Annotator(im0, line_width=2, example=names)

    if boxes is not None:
        for box, cls in zip(boxes, clss):
            annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])

            obj = im0[int(box[1]) : int(box[3]), int(box[0]) : int(box[2])]
            blur_obj = cv2.blur(obj, (blur_ratio, blur_ratio))

            im0[int(box[1]) : int(box[3]), int(box[0]) : int(box[2])] = blur_obj
    #----------------------------------------------------------------------------
    
    #OBJECT COUNTING CODE--------------------------------------------------------
    #tracks = model.track(im0, persist=True, show=False, tracker="bytetrack.yaml")
    im0 = counter.start_counting(im0, results) #im0 = counter.start_counting(im0, tracks)
    #---------------------------------------------------------------------------- 
    
    cv2.imshow("Preliminary Work", im0) #Will delete
    video_writer.write(im0) #Will delete
   
    if cv2.waitKey(1) & 0xFF == ord("q"): #To exit program loop
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()"""