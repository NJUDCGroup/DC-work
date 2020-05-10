#!coding=utf-8
import cv2 as cv
filepath = "/mnt/f/video/test2.rmvb"
cap = cv.VideoCapture(filepath)
if cap.isOpened():
    fps = cap.get(cv.CAP_PROP_FPS)    
    sleepTime = int(1000/fps)   
    print(sleepTime)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("can't receive frame (strea, end?). Exiting...")
        break
    cv.imshow('frame',frame)
    if cv.waitKey(sleepTime)==ord('q'):
        break
cap.release()
cv.destroyAllWindows()