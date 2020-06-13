#!coding=utf-8
import cv2 as cv
filepath = "../test.mp4"
cap = cv.VideoCapture(filepath)
if cap.isOpened():
    fps = cap.get(cv.CAP_PROP_FPS)  
    fourcc = cap.get(cv.CAP_PROP_FOURCC)
    width = cap.get(cv.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv.CAP_PROP_FRAME_HEIGHT)  
    sleepTime = int(1000/fps)   
    out = cv.VideoWriter('a.mp4',cv.VideoWriter_fourcc(*'MJPG'),fps,(int(width),int(height)))
    #sleepTime = 1
    print(fps)
else:
    print("no open")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("can't receive frame (strea, end?). Exiting...")
        break
    cv.imshow('frame',frame)
    out.write(frame)
    if cv.waitKey(sleepTime)==ord('q'):
        break
cap.release()
out.release()
cv.destroyAllWindows()
print('done!')