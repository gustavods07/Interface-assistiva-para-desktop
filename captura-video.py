import numpy as np
import cv2
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30) 
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('C:/Users/gusta/Documents/MESTRADO/output.mp4', fourcc, 30.0, (640,  480))
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if 'time' not in locals():
        time = cap.get(cv2.CAP_PROP_POS_MSEC)
        print("inicio",time)
 
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here 
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Display the resulting frame
    cv2.imshow('frame', frame)
    out.write(frame)
    if cv2.waitKey(1) == ord('a'):
        dur = int((cap.get(cv2.CAP_PROP_POS_MSEC) - time)/1000)
        print("duração",dur)
    if cv2.waitKey(1) == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
