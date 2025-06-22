#include <Servo.h>

// Define relay output pins
const int light1Pin = 2;
const int light2Pin = 3;
const int lockPin   = 8;
const int tvPin     = 7;

// Servo pins
const int curtainServoPin = 9;
const int fanServoPin = 4;

// Device states
bool light1State = false;
bool light2State = false;
bool lockState = false;
bool tvState = false;
bool curtainState = false;
bool fanState = false;

// Servo objects
Servo curtainServo;
Servo fanServo;

String command = "";

void setup() {
  Serial.begin(9600);

  // Set relay pins as output
  pinMode(light1Pin, OUTPUT);
  pinMode(light2Pin, OUTPUT);
  pinMode(lockPin, OUTPUT);
  pinMode(tvPin, OUTPUT);

  // Initialize relays as OFF (HIGH for active-low relays)
  digitalWrite(light1Pin, HIGH);
  digitalWrite(light2Pin, HIGH);
  digitalWrite(lockPin, HIGH);
  digitalWrite(tvPin, HIGH);

  // Attach servos
  curtainServo.attach(curtainServoPin);
  fanServo.attach(fanServoPin);

  // Set initial servo positions
  curtainServo.write(0);  // Curtains closed
  fanServo.write(0);      // Fan OFF
}

void loop() {
  // Read serial data
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') {
      handleCommand(command);
      command = "";
    } else {
      command += ch;
    }
  }
}

void handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "LIGHT1") {
    light1State = !light1State;
    digitalWrite(light1Pin, light1State ? LOW : HIGH);
  }
  else if (cmd == "LIGHT2") {
    light2State = !light2State;
    digitalWrite(light2Pin, light2State ? LOW : HIGH);
  }
  else if (cmd == "LOCK") {
    lockState = !lockState;
    digitalWrite(lockPin, lockState ? LOW : HIGH);
  }
  else if (cmd == "TV") {
    tvState = !tvState;
    digitalWrite(tvPin, tvState ? LOW : HIGH);
  }
  else if (cmd == "CURTAINS") {
    curtainState = !curtainState;
    curtainServo.write(curtainState ? 90 : 0);  // 90 = open, 0 = closed
  }
  else if (cmd == "FAN_ON") {
    fanState = true;
    fanServo.write(90);  // Fan ON
  }
  else if (cmd == "FAN_OFF") {
    fanState = false;
    fanServo.write(0);   // Fan OFF
  }
}
