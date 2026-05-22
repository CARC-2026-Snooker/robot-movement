# Repository File Structure
```
Project
├── ...
├── autorun.service         <-- Script that would run the Python script at Pi's startup.
├── Autista
|   ├── Autista.h           <-- Hallucinata's specific code.
|   ├── Autista.cpp
|   ├── Autista.ino
|   └── pi.py
├── Hallucinata             <-- Hallucinata's specific code.
|   ├── Hallucinata.ino
|   └── pi.py
└── library
    ├── arduino
    |   └── ...
    └── pi
        └── ...
```
The `Autista` / `Hallucinata` directory is where specific implementation of `BaseRobot` and Python script for running on the Pi are located.<br>
`.h` and `.cpp` declare and define the implementation of `BaseRobot` (probably the addition of ball launching code and ball picking code), while `.ino` is the final code that will be upload to Arduino.<br>
`pi.py` is a Python script for works that require a bit more performance compare to Arduino like image processing.
# Setting Up the Bobot
## Arduino
1. Copy the `arduino` directory located inside `library` directory into Arduino's library directory.
2. Upload the bobot's code (either Autista's or Hallucinata's .ino file) onto the Arduino of the robot.
## Raspberry Pi
- SPI Interface Part
- Code Part
    1. Clone the repository into Pi's home directory.
    2. Run `uv sync` to install all the required libraries for the Pi.
    3. Copy the `autorun.service` into `/etc/systemd/system/` directory of the Pi while using the `sudo`.

After following those steps, Raspberry Pi should automatically run the Python script by itself everytimes it boot up.<br>
If you want to run the script now, run `uv run .../pi.py` where ... is the bobot's directory.