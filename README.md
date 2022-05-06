# Airthings to Home Assistant via MQTT Discovery

This Python script will read sensor values from [Airthings](https://www.airthings.com/) environmental monitoring devices through Bluetooth Low Energy (BLE) and send those values to Home Assistant via an MQTT broker. This script includes [Home Assistant MQTT discovery](https://www.home-assistant.io/docs/mqtt/discovery/) so your sensors will automatically appear in Home Assistant if everything is set up correctly. Airthings monitoring products are interesting because they can monitor radon levels, which is a radioactive gas that can be found in homes and is thought to be a cause of lung cancer.

**NOTE**: _This script can be installed as a Home Assistant add-on by going to the following repository and following the instructions: [mjmccans/hassio-addon-airthings](https://github.com/mjmccans/hassio-addon-airthings)._


## Screenshot

The screenshot below shows an Airthings Wave Plus device as it appears in Home Assistant, including the sensors associated with the device.

![Screenshot of Airthings Device in the Home Assistant ](/screenshots/airthings_device.png)


## Hardware Requirements

* An Airthings Wave, Airthings Wave Plus, or Airthings Wave Mini.
* A Raspberry Pi 3/4 with built-in Bluetooth, or a Bluetooth adapter that supports Bluetooth Low Energy (BLE).


## Getting Started

The instructions below are for running this script on a RaspberryPi running Raspbian with built in bluetooth capabilities. These instructions should work for other systems as well, but may need to be tweaked accordingly.


## Dependencies

* Run the following commands to install pip for Python3 and then use pip3 to install the dependencies:
```
sudo apt install python3-pip
pip3 install --user paho-mqtt
pip3 install --user bluepy
```
* Run the following command to give permissions required for bluepy to interact with the bluetooth radio without being root:
``` 
sudo setcap 'cap_net_raw,cap_net_admin+eip' `find ~/.local/lib/ | grep bluepy-helper | grep -v bluepy-helper.c`
```

## Automatic Configuration

You can automatically scan for devices and generate a starting ```options.json``` by running the script with the ```--generate_config``` command line option. By default this will write an ```options.json``` file into the current directory that you can then tweak as needed:

```
./airthings-mqtt-ha.py --generate_config
```

As an alternative, if you run the script without a config file, or the config file does not contain any configured devices, then the script will scan for devices and output to the screen a suggested sample config file that you can tweak and use.


## Example Configuration

Below is an example ```options.json``` file.

```json
{
  "devices": [
    {
      "mac": "58:93:D8:8B:12:7C",
      "name": "Basement Office"
    }
  ],
  "refresh_interval": 150,
  "retry_count": 10,
  "retry_wait": 3,
  "log_level": "INFO",
  "mqtt_discovery": true,
  "mqtt_retain": false,
  "mqtt_host": "hass",
  "mqtt_username": "airthings",
  "mqtt_password": "secret"
}
```

## Configuration Options

The following are the options that can be included in the ```options.json``` file and what they do.


### Option: `devices`

The `devices` option sets out your Airthings devices. For each device you set out its `mac` address and a `name`. The `name` is used for the mqtt discovery feature so your devices and their associated sensors are given human readable and unique names. Below is an example of two devices being configured:

```json
  "devices": [
    {
      "mac": "58:93:D8:8B:12:7C",
      "name": "Basement Office"
    },
    {
      "mac": "8H:93:D8:8B:12:8F",
      "name": "Living Room"
    }
  ],
```

### Option: `refresh_interval`

This option sets how many seconds to wait before next refresh of the sensor data. Note that the sensors on the Airthings Wave + only update every 5 minutes, but the default has been set to half that to avoid delays in getting new sensor values.


### Option: `retry_count`

This option sets the number of times to retry accessing your Airthings devices when there is a bluetooth error or other issue before exiting. The default is 10, but you can increase this if you have reception or other issues.


### Option: `retry_wait`

This option sets the time, in seconds, to wait between the retries set out in `retry_count`.


### Option: `log_level`

The `log_level` option controls the level of log output and can be changed to be more or less verbose, which might be useful when you are dealing with an unknown issue. Possible values are:

`CRITICAL`, `ERROR`, `WARNING`, `INFO` or `DEBUG`


### Option: `mqtt_discovery`

This option controls whether the Home Assistant's MQTT Discovery feature is enabled or disabled. If disabled, you can configure the sensors individually and they will be located at mqtt topic `/airthings/<mac>/<sensor name>` where <mac> is the `mac` address you set for your device and `sensor name` is the name of the sensor from the device. For example, the sensor names for the Airthings Wave Plus are: `humidity`, `radon_1day_avg`, `radon_longterm_avg`, `temperature`, `rel_atm_pressure`, `co2` and `voc`.


### Option: `retain`

This option sets the "retain" flag for the sensor values sent to the MQTT broker. This means that the last sensor value will be retained by the MQTT broker, meaning that if you restart Home Assistant the last sensor values sent to the MQTT broker will show up immediately once Home Assistant restarts. The downside is that the sensor values may be out of date, particularly if the script has stopped. If you change this value to `false` the script will clear any existing retained values.


### Option: `mqtt_host`

This option sets out the hostname of your mqtt broker.


### Option: `mqtt_username`

This option sets out the username to use to access your mqtt broker.


### Option: `mqtt_password`

This option sets out the password to use to access your mqtt broker.


## Running as a Service

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

## Current Limitations

* This script has only been tested with a single Airthings Wave Plus device, but should work with multiple devices and with many other Airthings devices (although some testing and tweaks may be needed).
* Only metric units are supported at this time, although it should be easy to add unit conversion if desired.
* The Airthings devices must be connected to the official app at least once before you can use this script.
* Point in time radon levels are not made available through Bluetooth LE so they cannot be accessed by this script, but you can regularly get the 1 day and long term average measurements.

## Inspiration

As is often the case with open source software, this project would not have been possible without the hard work others. In particular, I have heavily leveraged the code developed by Marty Tremblay for his [sensor.airthings_wave](https://github.com/custom-components/sensor.airthings_wave) project for interacting with Airthings devices. If you find this Python script useful please head over to Marty's project and buy him a coffee or a beer. 

## Contributions and Feedback

Feedback, suggested changes and code contributions are welcome. I have not been a professional programmer for close to 20 years and my experience dates back to the Python 2.2 era, so it is possible that my code is behind the times or just simply wrong. I am open to constructive feedback and improvements, I love learning new things from the community, and I am willing to admit when I am wrong. That is the power of open source software, and all that I ask is that any feedback or comments are courteous and respectful and I will a endeavor to do same with my responses. If you do submit any code changes, you are deemed to have agreed that your changes will be licensed under the MIT License that covers the project. If you do not agree with that license, then please do not submit any code changes.
