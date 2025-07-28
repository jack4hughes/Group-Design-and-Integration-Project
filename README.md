# Project Overview:
This is a program to control a Lynxmotion robot arm using Python. This robot was designed to move test tubes from one rack to another in a smart lab environment. It was designed to be used by users with limited robotic experience and training, perform repeatable tasks, and operate safely and effectively.

Completed as part of UWE 3rd year GDIP group project.


# How to Run
To run this code, you will need a [LynxMotion 6DoF robotic arm](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/ses-v1/ses-v1-robots/ses-v1-arms/al5d/) with a [LynxMotion servo controller](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/servo-erector-set-system/ses-electronics/ses-modules/ssc-32/ssc-32-manual/).  Download the whole repository, 

## Steps:
- Connect your servo controller to your computer.
- Find the file location of your controller within /dev (it should begin with 'tty-usbserial').
- Change the string in LYNXMOTION_SERVO_CONTROLLER_LOC to your controller name.
- Uncomment the pi_pico_serial_out variable within the main loop in main.py if using a Pi Pico (Pi Pico functionality currently broken, use at your own risk!).
- Change Robot object instantiation to use pi_pico_serial_out if needed.

**TODO:** Add requirements.txt

# Features:
**Modular Design:**
This code was designed to be modular and easily swappable. This allowed the embedded system to be developed separately from the high-level Python controller, with control commands being able to be sent directly from a computer to the SM322 Serial board, or a Raspberry Pi Pico capable of saving a path and operating independently. The code was also designed to allow easy swapping of controllers, using an abstract Controller class, which specific implementations could inherit from.

All joint information was also stored in YAML files, which made it easy to change the length of individual joints or servo limits without editing code directly.

**Easy Control Using an Xbox Controller:** The robot was designed to use an Xbox controller for user input. Most people are familiar with a game controller, reducing the time needed to become accustomed to the system.
**Path Following:** The robot was designed to follow a specific path specified by the user using keypoint mapping. Users could move the robot to a specific position and save key points using an Xbox One Controller. Then, the robot would replay the keypoint path, smoothly interpolating between each keypoint using a chained iterator approach implemented within Python.

**Full FK and Workspace Limits:** To ensure safe operation, a full FK system was developed that allowed implementation of workspace limits in Cartesian space as well as limits in joint space, stopping the robot from crashing into the ground or walls during normal operation.







```
