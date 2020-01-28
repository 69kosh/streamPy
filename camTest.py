import cv2
from time import sleep

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 1)
winname = "Test"
cv2.namedWindow(winname)        # Create a named window
cv2.moveWindow(winname, 40,30)  # Move it to (40,30)

# while(True):
    # Capture frame-by-frame
    
ret, frame = cap.read()
print(('first', ret))
print(('first', frame))
# while not ret:
#     ret, frame = cap.read()
#     print(('next', ret))
#     ret, frame = cap.read()

    # Our operations on the frame come here
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
print(('gray', gray))
#     gray = frame
    # Display the resulting frame
cv2.imshow(winname, frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
cv2.waitKey(1)
# sleep(2)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()