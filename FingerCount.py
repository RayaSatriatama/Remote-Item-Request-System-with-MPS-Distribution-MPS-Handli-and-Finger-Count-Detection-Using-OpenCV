import time
import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports
import math
import numpy as np
import threading

# Function to list available serial ports
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = []
    for port in ports:
        available_ports.append(port.device)
    return available_ports


# Function to prompt user for port and baud rate
def setup_serial_connection():
    available_ports = list_serial_ports()

    if len(available_ports) == 0:
        print("No serial ports found.")
        return None

    print("Available Serial Ports:")
    for i, port in enumerate(available_ports):
        print(f"{i}: {port}")

    port_index = int(input(f"Select a port by number (0 to {len(available_ports) - 1}): "))
    selected_port = available_ports[port_index]

    baud_rate = input("Enter baud rate (default is 9600): ")
    if baud_rate == "":
        baud_rate = 9600
    else:
        baud_rate = int(baud_rate)

    try:
        serial_comm = serial.Serial(selected_port, baud_rate)
        serial_comm.timeout = 1
        print(f"Connected to {selected_port} at {baud_rate} baud rate.")
        return serial_comm
    except serial.SerialException as e:
        print(f"Error connecting to {selected_port}: {e}")
        return None


# Setup serial communication dynamically
serialComm = setup_serial_connection()

# Function to calculate movement distance
def calculate_movement(center1, center2):
    """
    Calculate the Euclidean distance between two center points (center1 and center2).
    """
    distance = math.sqrt((center2[0] - center1[0]) ** 2 + (center2[1] - center1[1]) ** 2)
    return distance

# Function to handle serial communication in a separate thread
def send_serial_value(serialComm, value):
    try:
        serialComm.write(f"{value}\n".encode())
    except Exception as e:
        print(f"Error sending data to serial: {e}")

# Hand Detector class
class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.7, minTrackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Little

    def findHands(self, img, draw=True, flipType=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    myHand["type"] = "Right" if handType.classification[0].label == "Right" else "Left"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 255), 2)
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 255), 2)
        return allHands, img

    def fingersUp(self, myHand):
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        fingers = []

        # Thumb Detection Improvement
        # We use relative distance from the wrist to the thumb tip for better detection
        wrist_index = 0
        thumb_tip = self.tipIds[0]
        index_mcp = 2  # MCP of index finger

        # Calculate the horizontal distance between the thumb and the wrist/index finger
        wrist_thumb_distance = abs(myLmList[thumb_tip][0] - myLmList[wrist_index][0])
        wrist_index_distance = abs(myLmList[index_mcp][0] - myLmList[wrist_index][0])

        if myHandType == "Right":
            # For right hand, thumb should be to the left of index for it to be considered "up"
            if wrist_thumb_distance > wrist_index_distance and myLmList[thumb_tip][1] < myLmList[index_mcp][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Left hand
            # For left hand, thumb should be to the right of index for it to be considered "up"
            if wrist_thumb_distance > wrist_index_distance and myLmList[thumb_tip][1] < myLmList[index_mcp][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # 4 Fingers (Index, Middle, Ring, Little)
        for id in range(1, 5):
            if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:  # Tip of finger higher than the joint
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

# Main function
def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.85, maxHands=2)  # Increased detection confidence
    nilai = 0
    buffer_size = 10  # Store the last 10 frames for finger counts
    finger_count_buffer = []

    previous_center = None  # Keep track of the previous center of the hand
    movement_threshold = 15  # Set a threshold for how much movement is allowed
    paused = False  # Start with the program not paused

    last_sent_value = None  # Track the last sent value to avoid repeated sends
    last_send_time = 0  # Track the last time the value was sent

    # Maximize the window (not fullscreen)
    cv2.namedWindow("image", cv2.WND_PROP_AUTOSIZE)
    cv2.setWindowProperty("image", cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 1280, 720)  # Resize window to a large size

    while True:
        if not paused:
            success, img = cap.read()
            if not success:
                print("Failed to capture video")
                break

            hands, img = detector.findHands(img)

            totalFingers1 = totalFingers2 = 0
            if hands:
                hand1 = hands[0]
                current_center = hand1["center"]  # Get the center point of the hand

                # If we have a previous center, calculate the movement
                if previous_center:
                    movement = calculate_movement(previous_center, current_center)
                else:
                    movement = 0  # No movement for the first frame

                # Update the previous center point
                previous_center = current_center

                # If the hand moves less than the threshold, take the finger count
                if movement < movement_threshold:
                    totalFingers1 = detector.fingersUp(hand1).count(1)

                    if len(hands) == 2:
                        hand2 = hands[1]
                        totalFingers2 = detector.fingersUp(hand2).count(1)

                        # Ensure both hands are not counted if they are the same type
                        if hand1["type"] == hand2["type"]:
                            totalFingers2 = 0

                    # Smoothing the finger counts over multiple frames for accuracy
                    finger_count = totalFingers1 + totalFingers2
                    finger_count_buffer.append(finger_count)

                    # Keep only the last 10 counts
                    if len(finger_count_buffer) > buffer_size:
                        finger_count_buffer.pop(0)

                    # Calculate the average finger count from the buffer to stabilize results
                    smoothed_finger_count = int(np.mean(finger_count_buffer))
                else:
                    # If movement is too high, do not update the count (hand is moving)
                    smoothed_finger_count = nilai

            else:
                smoothed_finger_count = 0

            # Update serial if finger count changes, with delay, and movement is within threshold
            current_time = time.time()
            if nilai != smoothed_finger_count:
                nilai = smoothed_finger_count

                # Send the new value and update the last sent value and time
                last_sent_value = nilai
                last_send_time = current_time

                print(f"Number of fingers: {nilai}")
                if serialComm:
                    # Send the value to serial in a separate thread
                    threading.Thread(target=send_serial_value, args=(serialComm, nilai)).start()

            # Ensure a 0.5 second delay before sending a new value
            elif current_time - last_send_time >= 0.5 and last_sent_value is not None:
                last_send_time = current_time  # Update the last send time
                if serialComm:
                    threading.Thread(target=send_serial_value, args=(serialComm, last_sent_value)).start()

        # Display the number of fingers in the corner (always visible)
        cv2.putText(img, f'Number of fingers: {nilai}', (20, 440), cv2.FONT_HERSHEY_PLAIN, 1.8, (0, 255, 255), 2)

        # Display pause/play state on the video feed
        if paused:
            # To avoid overlapping text, draw the "PAUSED" text once with a proper background color
            cv2.rectangle(img, (20, 20), (150, 80), (0, 0, 0), -1)  # Background for text
            cv2.putText(img, "PAUSED", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            cv2.putText(img, "PLAYING", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Keybind Legend
        cv2.putText(img, "Keybinds:", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(img, "P - Pause/Play", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, "Q - Quit", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("image", img)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            paused = not paused  # Toggle paused state

    cap.release()
    cv2.destroyAllWindows()
    if serialComm:
        serialComm.close()

if __name__ == "__main__":
    main()
