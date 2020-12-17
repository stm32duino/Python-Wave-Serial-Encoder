# Python Wave Serial Encoder

## Manual
1. Use the dropdown menu to select the port and then click on *Connect*.
2. Choose the path where the file will be saved by using the *Save* button.
3. Use *Start* and *Stop* button to respectively start and stop the recording.

**Please note: to record more than one file, change the path else the old file will be overridden.**

In case the dropdown menu does not detect the port, use the button *Refresh* to update the Serial Port.

## Installation
The script has some python packages dependencies. Install them by running:

On Window:

	Tkinter is included in the Python standard library from version 3.1
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade -r requirements.txt

On Linux:

	sudo apt-get install python-tk python3-tk tk-dev python3-pip
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade -r requirements.txt