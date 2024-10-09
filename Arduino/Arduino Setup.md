# Arduino Relay Control with Serial Feedback

This project controls a relay via serial commands sent to an Arduino. The relay toggles on and off a certain number of times based on the serial input received. Feedback is provided from an external pin (pin 7) to ensure the relay process does not repeat unnecessarily. This project also integrates an input pin (pin 5) as an additional condition to enable or disable the relay control.

## Features

- **Relay control**: Toggle a relay connected to pin 2, based on serial commands.
- **Input control**: Only activate relay control if the input on pin 5 is HIGH.
- **Feedback signal**: The relay cycle waits for feedback from pin 7 before resetting, preventing repeated processing of the same command.
- **Serial communication**: Send commands through the serial interface to control the relay. Valid commands are numbers between 1 and 10.

## Hardware Requirements

- Arduino board (e.g., Uno, Nano, etc.)
- Relay module connected to pin 2
- External input (e.g., button or switch) connected to pin 5
- Feedback signal connected to pin 7
- Serial communication via USB (through the Arduino IDE)

## Pin Connections

- **Pin 2**: Connected to the relay module.
- **Pin 5**: Input pin to enable relay control. Must be HIGH to allow serial commands to control the relay.
- **Pin 7**: Feedback pin to reset the relay process once the relay toggling is completed.
