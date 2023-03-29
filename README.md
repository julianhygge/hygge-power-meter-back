# Hygge Power Meter

Hygge Power Meter is a software application that reads register data from different implementations of power meters. To work with this software, the power meter implementations must implement the contract `PowerMeterContract`.

## Creation of Debian package

To create a Debian package for the Hygge Power Meter software, follow these steps:

1. Create a new folder called `build`.
3. Copy the `hygge-power-meter` folder into the `build` folder, and navigate to the `hygge-power-meter` folder.
4. From within the `hygge-power-meter` folder, run the following command to create the Debian package: `dpkg-buildpackage -b`.

## Installation and use

5. Navigate to the folder created in step 1, where you should find the Debian package file.
6. Install the package by running the following command, replacing `XXXXX` with the actual version number: `sudo apt install ./hyggepowermeter_XXXXX.deb`.
7. The installation process will create two directories: `/var/lib/hyggepowermeter` (the working directory) and `/var/log/hyggepowermeter/` (the log directory).
8. To check the status of the service program, run the following command: `systemctl enable hyggepowermeter.service`.

When you run the Hygge Power Meter software for the first time, it will automatically create a config file and a database for each power meter implementation in the working directory. The default configuration parameters will be used to create the config file. If you need to modify any of these parameters, you can edit the config file and restart the service.
