#include <Servo.h>

// Create a Servo object
Servo myServo;

// Define the pins and angles
const int servoPin = 9;  // Pin connected to the servo control wire
const int minAngle = 0; // Minimum angle (0 degrees)
const int maxAngle = 90; // Maximum angle (180 degrees)
const int delayTime = 500; // Delay time between movements (in milliseconds)

int value = 0;

void setup() {
  // Attach the servo to the specified pin
  myServo.attach(servoPin);
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}

void loop() {
  // Move the servo to the minimum angle

  if (Serial.available() > 0) {
    // Read the incoming byte
    value = Serial.parseInt();
  }

  if (value == 1) {
    digitalWrite(13, HIGH);
    for(int i = 0; i < 5; i++) {
      myServo.write(minAngle);
      delay(delayTime); // Wait for the servo to reach the position

      // Move the servo to the maximum angle
      myServo.write(maxAngle);
      delay(delayTime); // Wait for the servo to reach the position
    }
    myServo.write(minAngle);
  }

  if (value == 0) {
    digitalWrite(13, LOW);
    myServo.write(minAngle);
    delay(delayTime); // Wait for the servo to reach the position
  }

}