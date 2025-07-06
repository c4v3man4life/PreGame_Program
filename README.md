Pregame MAC Address Utility

This Python3 tool helps you safely change your network interface's MAC address to a pre-approved ("good") OUI, or to any valid address you provide, using macchanger and standard Linux networking utilities. It can also create an operation directory for your workflow if needed.

Features

Checks that required tools (macchanger, iw, ip) are installed

Lists available network interfaces

Displays current MAC address and flags if it is a "good" or "bad" OUI

Allows changing the MAC address (random "good" or user-supplied)

Logs all actions and errors to pregame.log

Optionally creates an operation directory (uses MakeOp.create_directory)

Usage

Requirements

Python 3

Linux system with sudo privileges

Tools: macchanger, iw, ip (install via your package manager if missing)

Setup

Clone/download this repo and cd into it

(Optional) Ensure your Python virtual environment is activated

Ensure dependencies are installed:sudo apt install macchanger iw iproute2

(Optional) Adjust GOOD_OUIS in pregame.py to your approved OUIs

Run:

python3 pregame.py

Typical Workflow

Choose whether to create a new operation directory

Select which network interface you want to manage

View your current MAC and OUI status

If flagged as "BAD", choose to randomize to a "good" MAC or enter your own

Logging

All major events and errors are written to pregame.log

Troubleshooting

If you see missing tool errors, run sudo apt install macchanger iw iproute2

Must run as a user with sudo rights for MAC changes

Make sure your network interface is not in use by other programs during change
