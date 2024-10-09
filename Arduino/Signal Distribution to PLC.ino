String data_serial_receive;
int relay = 2;
int inputrelay = 5;
int feedbackPin = 7;  // Feedback pin
int a = 0;
int waktu = 50;

void setup() {
  Serial.begin(9600);
  pinMode(relay, OUTPUT);
  pinMode(inputrelay, INPUT);
  pinMode(feedbackPin, INPUT);  // Set feedback pin as input
  
  // Initial message in the Serial Monitor
  Serial.println("Program started. Waiting for serial input...");
}

void loop() {
  digitalWrite(relay, LOW);  // Ensure relay is off by default
  a = 0;

  // Check if inputrelay is HIGH
  if (digitalRead(inputrelay) == HIGH) {
    Serial.println("Input relay HIGH, waiting for serial data...");

    // Check if serial data is available
    if (Serial.available() > 0 && Serial.available() <= 10) {
      data_serial_receive = Serial.readStringUntil('\n');
      Serial.print("Data received: ");
      Serial.println(data_serial_receive);

      // Convert serial data to an integer
      int receivedNumber = data_serial_receive.toInt();

      // If the received number is between 1 and 10, control the relay accordingly
      if (receivedNumber >= 1 && receivedNumber <= 10) {
        Serial.print("Turning relay ON and OFF ");
        Serial.print(receivedNumber);
        Serial.println(" times.");
        
        for (a = 0; a <= receivedNumber; a++) {
          digitalWrite(relay, HIGH);
          delay(waktu);
          digitalWrite(relay, LOW);
          delay(waktu);
        }

        Serial.println("Relay cycle completed.");

        // Wait for feedback signal on pin 7 before resetting
        Serial.println("Waiting for feedback from pin 7...");
        while (digitalRead(feedbackPin) == LOW) {
          // Wait here until feedback signal is received (assumes HIGH is the signal)
        }
        Serial.println("Feedback received, resetting process...");
        
        // Reset the serial data to avoid repeated execution
        data_serial_receive = "";
      } else {
        Serial.println("Invalid data. Please enter a number between 1 and 10.");
      }
    }
  } else {
    // If inputrelay is LOW, still check serial data
    if (Serial.available() > 0) {
      data_serial_receive = Serial.readStringUntil('\n');
      if (data_serial_receive != "0") {
        digitalWrite(relay, LOW);
        Serial.println("Input relay LOW. Relay remains OFF.");
      }
    }
  }
}
