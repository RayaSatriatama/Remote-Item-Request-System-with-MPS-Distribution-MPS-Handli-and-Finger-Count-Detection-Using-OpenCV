# Hand Recognition for MPS Handling and Distribution using OpenCV

This project is designed to recognize hand gestures using a webcam and Mediapipe's hand detection model, integrated with OpenCV. The program counts the number of fingers visible and sends this data over a serial communication interface (e.g., to control microcontroller-based systems). The program is optimized for real-time hand recognition and efficiently handles serial communication without repeated or redundant transmission of data.

## Features

- Real-time hand detection using a webcam and Mediapipe.
- Detection and counting of fingers, even with varying hand orientations (flipped or upright).
- Visual feedback with a bounding box around detected hands and a counter showing the number of detected fingers.
- Serial communication (`serialComm`) to transmit the finger count for external handling.
- Efficient transmission over the serial port, ensuring that data is only sent when the count changes, and no redundant transmission occurs.
- A pause/play function to temporarily stop hand detection, useful for control applications.

## Requirements

Ensure that you have the following dependencies installed to run the project:

- Python 3.8+
- OpenCV
- Mediapipe
- PySerial
- Numpy

### Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/Hand-Recognition-MPS-Handling.git
   cd Hand-Recognition-MPS-Handling
   ```

2. Create a new environment using `conda` or `venv` and activate it:
   ```bash
   conda create --name hand-recognition python=3.8
   conda activate hand-recognition
   ```

3. Install the required dependencies:
   ```bash
   pip install opencv-python mediapipe pyserial numpy
   ```

## Running the Program

1. Ensure your camera is connected.
2. Connect the serial device (e.g., Arduino, microcontroller, for testing camera its optional) to your machine.
3. Run the main Python script:
   ```bash
   python fingercount.py
   ```

### Keybinds

- **P**: Pause/Play hand detection.
- **Q**: Quit the program.

## How It Works

1. **Hand Detection**:
   - The program uses Mediapipe’s hand tracking model to detect hands in real time through a webcam.
   - It draws landmarks on the hand and calculates how many fingers are extended based on the positions of specific landmarks.

2. **Finger Counting**:
   - It detects if the thumb and fingers are raised or closed using specific landmark positions.
   - Works with both left and right hands, even when flipped or rotated.

3. **Serial Communication**:
   - The program sends the count of raised fingers via serial communication (e.g., COM ports).
   - Data is sent only when the finger count changes to avoid redundant transmissions.
   - Uses a 0.5-second delay between sends to ensure smooth communication.

### Sample Output

- The program displays the webcam feed with a bounding box around detected hands.
- It displays the type of hand detected (left or right) and the number of fingers raised.
- Serial data is sent asynchronously in the background to avoid lag.

## Example Use Case

This project is ideal for applications where hand gestures need to be interpreted by a microcontroller or other hardware via serial communication. For example:

- **Industrial MPS Handling**: The system can be used to control and monitor machines, signal distributions, or commands using hand gestures.
- **Control Interfaces**: Replace physical buttons with gesture controls, providing a touch-free interface.
- **Automation Systems**: Use hand recognition to trigger certain actions in automation or robotics.

## Troubleshooting

### Video Lag or Slow Response
- Ensure that the serial communication is working efficiently and that the baud rate is set to an appropriate value (e.g., 115200).
- Try reducing the video frame size or disabling other processes that might interfere with real-time detection.

### Serial Communication Issues
- Ensure that the correct COM port or serial device is selected. You can list available ports in the code to make sure the right one is chosen.
- Make sure that the device connected to the serial port is powered and configured correctly.
