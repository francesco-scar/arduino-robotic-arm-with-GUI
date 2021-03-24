# Arduino Robotic Arm with GUI

# Introduction

This Arduino sketch control a 6 DOF (Degrees Of Freedom) robotic arm using a GUI running on the PC that send commands via USB connection.

The GUI has 6 sliders to set the position of each servo in real time, and buttons to save the current position, delete previous saved position end execute saved position.

Each saved position is also saved in internal EEPROM and if the arduino don't receive expected startup handshake (sent by the GUI) in 5 seconds it starts executing positions saved in the EEPROM.

This project is similar to [arduino-robotic-arm-braccio](https://github.com/francesco-scar/arduino-robotic-arm-braccio).


# Configuration

Servo pins are defined at line [11](https://github.com/francesco-scar/arduino-robotic-arm-with-GUI/blob/73f88d63184bdbbb1b2adfee6bd9be493d2ca803/Robotic_arm_arduino_sketch/Robotic_arm_arduino_sketch.ino#L11) and following.
```c++
#define SERVO1 2
#define SERVO2 3
#define SERVO3 4
#define SERVO4 5
#define SERVO5 6
#define SERVO6 7
```

Move in the directory where you downloaded the program and run the GUI with `python3 Kivy_GUI.py`.
You might need to install `kivy` and `pyserial` with `pip3 install kivy` and `pip3 install pyserial`.

Once the GUI is running just connect the Arduino trough the USB port and the program will automatically connect to it and open a window with the sliders and buttons.
