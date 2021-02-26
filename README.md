# Airthings to Home Assistant via MQTT Discovery

This Python script will read sensor values from [Airthings](https://www.airthings.com/) environmental monitoring devices through Bluetooth Low Energy (BLE) and send those values to Home Assistant via an MQTT broker. This script includes [Home Assistant MQTT discovery](https://www.home-assistant.io/docs/mqtt/discovery/) so your sensors will automatically appear in Home Assistant if everything is set up correctly. Airthings monitoring products are interesting because they can monitor radon levels, which is a radioactive gas that can be found in homes and is thought to be a cause of lung cancer.

## Screenshot

The screenshot below shows an Airthings Wave Plus device as it appears in Home Assistant, including the sensors associated with the device.

![Screenshot of Airthings Device in the Home Assistant ](/screenshots/airthings_device.png)

## Inspiration

As is often the case with open source software, this project would not have been possible without the hard work others. In particular, I have heavily leveraged the code developed by Marty Tremblay for his [sensor.airthings_wave](https://github.com/custom-components/sensor.airthings_wave) project for interacting with Airthings devices. If you find this Python script useful please head over to Marty's project and buy him a coffee or a beer. 

## Getting Started

The instructions below are for running this script on a RaspberryPi running Raspbian with built in bluetooth capabilities. These instructions should work for other systems as well, but may need to be tweaked accordingly.

### Pre-requisites

* Run the following commands to install pip for Python3 and then use pip3 to install the dependencies:
```
sudo apt install python3-pip
pip3 install --user paho-mqtt
pip3 install --user pygatt
pip3 install --user pexpect
```
* Run the following command to give permissions required for pygatt to interact with the bluetooth radio:
``` 
sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`
```

### Configure the script

* Update the ```config.toml``` file to reflect your needs. Further details are provided in comments in the ```config.toml``` file to help guide you. 
* As noted in the ```config.toml``` file, to search for your your Airthings devices comment out the ```[[devices]]``` block, which will cause the script to search for devices and the mac address of any devices found will be output.
* Once you have the relevant mac addresses, it is recommended to update the ```[[devices]]``` block so that a scan is not required on each run.
* In order for Home Assistant MQTT discovery to work, you will need to update the remainder of the ```[[devices]]``` block to reflect your device's sensors and how you want them to appear in Home Assistant. Note that a Home Assistant MQTT discovery message is sent to the MQTT broker once each time the script is run, so you can always update the details and they will be reflected in Home Assistant the next time the script is run.

### Running as a Service

Once you have all the kinks worked out and the script is working as expected, you may want to run the script as a systemd service. To do so you can use the example systemd unit file found in the ```systemd``` directory of this repository as an example. To use it do the following:

* Copy the file ```airthings-mqtt-ha.service``` found in the systemd directory of this repository into your ```/etc/systemd/system/``` directory.
* Update the ```airthings-mqtt-ha.service``` file to reflect your usernames and paths.
* Run the following commands as fit for your purposes:

```
# Start the airthings-mqtt-ha script
sudo systemctl start airthings-mqtt-ha

# Have the airthings-mqtt-ha service start on boot
sudo systemctl enable airthings-mqtt-ha
```
* Finally, you can check on the status of the script by running either of the following commands:

```
sudo systemctl status airthings-mqtt-ha

sudo service airthings-mqtt-ha status
```

## Hardware Requirements

* An Airthings Wave, Airthings Wave Plus, or Airthings Wave Mini.
* A Raspberry Pi 3/4 with built-in Bluetooth, or a Bluetooth adapter that supports Bluetooth Low Energy (BLE).

## Current Limitations

* This script has only been tested with a single Airthings Wave Plus device, but should work with multiple devices
and with many other Airthings devices (although some testing and tweaks may be needed).
* Only metric units are supported at this time, although it should be easy to add unit conversion if desired.
* The Airthings devices must be connected to the official app at least once before you can use this script.
* Point in time radon levels are not made available through Bluetooth LE so they cannot be accessed by this script, but you can regularly get the 1 day and long term average measurements.

## Contributions and Feedback

Feedback, suggested changes and code contributions are welcome. I have not been a professional programmer for close to 20 years and my experience dates back to the Python 2.2 era, so it is possible that my code is behind the times or just simply wrong. I am open to constructive feedback and improvements, I love learning new things from the community, and I am willing to admit when I am wrong. That is the power of open source software, and all that I ask is that any feedback or comments are courteous and respectful and I will a endeavor to do same with my responses. If you do submit any code changes, you are deemed to have agreed that your changes will be licensed under the MIT License that covers the project. If you do not agree with that license, then please do not submit any code changes.