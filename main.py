import numpy as np
import cv2
import time
import pandas as pd
import requests
import json
import io


# my local camera gives me 28-30 fps, if i want to compute the OCR every 3 seconds ==> set target to 90


def most_common(lst):  # returns the most common item in a list
    return max(set(lst), key=lst.count)


def detectContainerId(img):  # function that sends the current frame to the API and opply the OCR on it
    height, width, _ = img.shape
    # Cutting image
    roi = img[0: height, 0: width]
    # Ocr
    url_api = "https://api.ocr.space/parse/image"
    _, compressedimage = cv2.imencode(".jpg", roi, [1, 90])
    file_bytes = io.BytesIO(compressedimage)
    result = requests.post(url_api, files={"screenshot.jpg": file_bytes},
                           data={"apikey": "f71cc68fcd88957", "language": "eng", "OCREngine": 2})
    result = result.content.decode()
    result = json.loads(result)
    parsed_results = result.get("ParsedResults")[0]
    text_detected = parsed_results.get("ParsedText")
    text_detected = text_detected.splitlines()
    containerID = None
    for text in text_detected:
        containerID = text
    return containerID


# def calculate_time(start, end):
#     return end - start
database = pd.read_csv('plates.csv')
df = pd.DataFrame(columns=['plate_number', 'time'])

cap = cv2.VideoCapture('actual.mp4')

max_array_size = 7
target = 60
frame_counter = 0

# start_time = time.time()
# end_time = 0
plates = []

# time_of_arrival = 0

while True:
    # Capture frame-by-frame
    frame_counter += 1
    # start_time = time.time()
    ret, frame = cap.read()

    # if video finished or no Video Input
    if not ret:
        break

    response = ''  # we will store the OCR results in this variable
    # Our operations on the frame come here
    if frame_counter == target:
        frame_counter = 0
        # end_time = time.time()
        # print(f"{target} FPS took {calculate_time(start_time, end_time)} seconds")

        # start_time = end_time

        # API PART
        response = detectContainerId(frame)
        print(response)

        if response != 'None':
            plates.append(response)
            if len(plates) == 1:  # first time we scanned and found the OCR is when the truck arrived
                time_of_arrival = time.time()
            if len(plates) == max_array_size:  # get the OCR with most occurrences and then store it in the dataframe
                correct_plate = most_common(plates)
                threshold = plates.count(correct_plate)
                if threshold < 4:  # this means that at most, 3/7 results scanned were MAYBE accurate.
                    print('The readings were not accurate! Please try again and make sure the vehicle is not moving!')
                    plates.clear()
                # print(correct_plate)
                elif len(plates) > max_array_size:
                    pass
                else:
                    print(f'Scanning done. Plate number: {correct_plate}')
                    # creating a new row and adding it to the dataframe
                    df = pd.concat(
                        [df, pd.DataFrame.from_records([{'plate_number': correct_plate, 'time': time_of_arrival}])],
                        axis=0)
                    # real time changes on the database
                    updated_db = pd.concat([database, df])
                    updated_db.to_csv('plates.csv')


        else:  # meaning the result was 'None' and no plates were found
            if len(plates) > 0:
                print('The process was cut midway, please dont leave before process is over. PROCESS RESTARTING')
                plates.clear()
            else:
                print('No plate found')
                if len(plates) >= max_array_size:
                    plates.clear()
                    print('Ready to accept new plate number')

    if cv2.waitKey(1) & 0xFF == ord('q'):  # press 'q' on the keyboard to exit
        break

    cv2.imshow('Frame', frame)

print(df)
# # creating the resulting Dataframe
# df.to_csv('plates.csv')
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
