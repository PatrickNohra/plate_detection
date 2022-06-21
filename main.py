import numpy as np
import cv2
import time
import pandas as pd

# my local camera gives me 28-30 fps, if i want to compute the OCR every 3 seconds ==> set target to 90

cap = cv2.VideoCapture('2.mp4')

target = 150
frame_counter = 0


def calculate_time(start, end):
    return end - start


# Create the csv file
df = pd.DataFrame({'plate_number': [], 'time': []})
df.to_csv('plates.csv', index=True)

# How to add a row in the dataframe

# new_row = {'plate_number': 0, 'time': 120}
# new_row2 = {'plate_number': 2, 'time': 222}
#
# df = df.append(new_row, ignore_index = True)
# df = df.append(new_row2, ignore_index = True)

# appending new data to the csv file
df.to_csv('plates.csv', mode='a')

start_time = time.time()
end_time = 0
while True:
    # Capture frame-by-frame
    frame_counter += 1
    # start_time = time.time()
    ret, frame = cap.read()

    # if video finished or no Video Input
    if not ret:
        break
    frame = cv2.resize(frame, (520,720))
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # Our operations on the frame come here
    if frame_counter == target:
        end_time = time.time()
        # Place the OCR code here
        print(f"{target} FPS took {calculate_time(start_time, end_time)} seconds")
        frame_counter = 0
        start_time = end_time

    # get the read number of of the plate and store it in ...? a Dataframe?

    # if no plate found after 10 seconds, store the temp variable in a dataframe with the correct time

    if cv2.waitKey() & 0xFF == ord('q'):  # press 'q' on the keyboard to exit
        break

    cv2.imshow('Frame', frame)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print(time.time())
