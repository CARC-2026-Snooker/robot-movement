# Repository File Structure
```
Project
├── ...
├── autorun.service         <-- Script that would run the Python script at Pi's startup.
├── Autista                 <-- Autista's specific code.
|   └── main.py
├── Hallucinata             <-- Hallucinata's specific code.
|   └── main.py
└── library                 <-- Python library files.
    └── ...
```
# Setting Up the Bobot
1. Clone the repository into Pi's home directory.
2. Run `uv sync` to install all the required libraries for the Pi.
3. Copy the `autorun.service` into `/etc/systemd/system/` directory of the Pi while using the `sudo`.

After following those steps, Raspberry Pi should automatically run the Python script by itself everytimes it boot up.<br>
If you want to run the script now, run `uv run .../pi.py` where ... is the bobot's directory.