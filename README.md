# NASA-USLI-2023-Electrical-Payload


Welcome!

This repository is still in progress and houses the majority of the camera integration/functionality code for the NASA USLI 2023 Competition

Action items as of 9/25/2022:
- Add modular methods so other parts of the program can be run (i.e. "img2BW" "applySobel")
- Figure out how to do command line prompting to run the program so RF payload can use our program
- Prompt program to run with "[Radio Callsign] B2 A1 C3 D4 ..."
- Pick out and purchase microcontroller and antenna design
- Integrate camera to a microcontroller and upload code to microcontroller to run on boot (similar to systemctl)
- Have RF transmissions dictate the microcontroller operations of when to take pictures and apply filters (to be decided by RF Payload subsystem)
- Build antenna to send RF transmissions
- House camera payload in chassis to be determined by Mechanical Payload Team
