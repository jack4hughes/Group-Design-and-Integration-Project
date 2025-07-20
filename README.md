A program to control a Lynxmotion robot arm in python.

Main Features:
The flexible design allows the program to operate on the robot using the SM322 Serial board, or a flashed Raspberry Pi Pico to control the arm.
- Full controller support for Xbox One controller or later. (Other controllers can be added, but this will have to be implemented by the user)
- Flexible robot config using YAML files.
- full FK for the robotic arm, with joint and workspace limits.
- Teach mode, allowing the robot to perform repeated actions once taught by the user.
  
Completed as part of UWE 3rd year GDIP project.

To actually run this code, you will need a [LynxMotion 6DoF robotic arm](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/ses-v1/ses-v1-robots/ses-v1-arms/al5d/) with a [LynxMotion servo controller](https://wiki.lynxmotion.com/info/wiki/lynxmotion/view/servo-erector-set-system/ses-electronics/ses-modules/ssc-32/ssc-32-manual/).

You can the group report for this arm in report.pdf in this document. Other members of the group included 
