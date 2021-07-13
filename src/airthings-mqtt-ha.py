#!/usr/bin/python3
#
# Copyright (c) 2021 Mark McCans
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging, time, json, sys, os, toml
import paho.mqtt.publish as publish
from paho.mqtt import MQTTException
from airthings import AirthingsWaveDetect
# DEBUG: Remove old imports
#from pygatt.exceptions import NotConnectedError, BLEError, NotificationTimeout

_LOGGER = logging.getLogger("airthings-mqtt-ha")

CONFIG = {}     # Variable to store configuration
DEVICES = {}    # Variable to store devices

# Default configuration values
CONFIG_DEFAULTS = {
    "general": {"refresh_interval": 150, "retry_count": 10, "retry_wait": 3, "log_level": "INFO"},
    "devices": [],
    "sensors": [],
    "mqtt": {"host": "localhost", "port": 1883}
}

class ATSensors:

    sensors_list = []

    def __init__(self, scan_interval, devices=None):
        _LOGGER.info("Setting up Airthings sensors...")
        self.airthingsdetect = AirthingsWaveDetect(scan_interval, None)
        # Note: Doing this so multiple mac addresses can be sent in instead of just one.
        if devices is not None and devices != {}:
            self.airthingsdetect.airthing_devices = list(devices)
        else:
            _LOGGER.info("No devices provided, so searching for sensors...")
            self.find_devices()
        
        # Get info about the devices
        if not self.get_device_info():
            # Exit if setup fails
            _LOGGER.error("Failed to set up Airthings sensors. Exiting.")
            sys.exit(1)

        _LOGGER.info("Done Airthings setup.")

    def find_devices(self):
        try:
            _LOGGER.debug("Searching for Airthings sensors...")
            num_devices_found = self.airthingsdetect.find_devices()
            _LOGGER.debug("Found {} airthings device(s)".format(num_devices_found))
            if num_devices_found != 0:
                # Put found devices into DEVICES variable
                for d in self.airthingsdetect.airthing_devices:
                    DEVICES[d] = {}
            else:
                # Exit if no devices found
                _LOGGER.warning("No airthings devices found. Exiting.")
                sys.exit(1)
        except:
            _LOGGER.exception("Failed while searching for devices. Exiting.")
            sys.exit(1)

    def get_device_info(self):
        _LOGGER.debug("Getting info about device(s)...")
        for attempt in range(CONFIG["general"]["retry_count"]):
            try:
                devices_info = self.airthingsdetect.get_info()
            #except (NotificationTimeout, NotConnectedError):
            #    _LOGGER.warning("Bluetooth error on attempt {}. Retrying in {} seconds.".format(attempt+1, CONFIG["general"]["retry_wait"]))
            #    time.sleep(CONFIG["general"]["retry_wait"])
            except:
                _LOGGER.exception("Unexpected exception while getting device information.")
                return False
            else:
                # Success!
                break
        else:
            # We failed all attempts
            _LOGGER.exception("Failed to get info from devices after {} attempts.".format(CONFIG["general"]["retry_count"]))
            return False

        # Collect device details
        for mac, dev in devices_info.items():
            _LOGGER.info("{}: {}".format(mac, dev))
            DEVICES[mac]["manufacturer"] = dev.manufacturer
            DEVICES[mac]["serial_nr"] = dev.serial_nr
            DEVICES[mac]["model_nr"] = dev.model_nr
            DEVICES[mac]["device_name"] = dev.device_name

        _LOGGER.debug("Getting sensors...")
        for attempt in range(CONFIG["general"]["retry_count"]):
            try:
                devices_sensors = self.airthingsdetect.get_sensors()
            #except (NotificationTimeout, NotConnectedError):
            #    _LOGGER.warning("Bluetooth error on attempt {}. Retrying in {} seconds.".format(attempt+1, CONFIG["general"]["retry_wait"]))
            #    time.sleep(CONFIG["general"]["retry_wait"])
            except:
                _LOGGER.exception("Unexpected exception while getting sensors information.")
                return False
            else:
                # Success!
                break
        else:
            # We failed all attempts
            _LOGGER.exception("Failed to get info from sensors after {} attempts.".format(CONFIG["general"]["retry_count"]))
            return False

        # Collect sensor details
        for mac, sensors in devices_sensors.items():
            for sensor in sensors:
                self.sensors_list.append([mac, sensor.uuid, sensor.handle])
                _LOGGER.debug("{}: Found sensor UUID: {} Handle: {}".format(mac, sensor.uuid, sensor.handle))
        
        return True
    
    def get_sensor_data(self):
        _LOGGER.debug("Getting sensor data...")
        for attempt in range(CONFIG["general"]["retry_count"]):
            try:
                sensordata = self.airthingsdetect.get_sensor_data()
                return sensordata
            #except (NotificationTimeout, NotConnectedError):
            #    _LOGGER.warning("Bluetooth error on attempt {}. Retrying in {} seconds.".format(attempt+1, CONFIG["general"]["retry_wait"]))
            #    time.sleep(CONFIG["general"]["retry_wait"])
            except:
                _LOGGER.exception("Unexpected exception while getting sensor data.")
                return False
            else:
                # Success!
                break
        else:
            # We failed all attempts
            _LOGGER.exception("Failed to get sensor data after {} attempts.".format(CONFIG["general"]["retry_count"]))
            return False
        
        return True

def mqtt_publish(msgs):
    # Publish the sensor data to mqtt broker
    try:
        _LOGGER.info("Sending messages to mqtt broker...")
        if "username" in CONFIG["mqtt"] and CONFIG["mqtt"]["username"] != "" and "password" in CONFIG["mqtt"] and CONFIG["mqtt"]["password"] != "":
            auth = {'username':CONFIG["mqtt"]["username"], 'password':CONFIG["mqtt"]["password"]}
        else:
            auth = None
        publish.multiple(msgs, hostname=CONFIG["mqtt"]["host"], port=CONFIG["mqtt"]["port"], client_id="airthings-mqtt", auth=auth)
        _LOGGER.info("Done sending messages to mqtt broker.")
    except MQTTException as e:
        _LOGGER.error("Failed while sending messages to mqtt broker: {}".format(e))
    except:
        _LOGGER.exception("Unexpected exception while sending messages to mqtt broker.")

if __name__ == "__main__":
    logging.basicConfig()
    _LOGGER.setLevel(logging.INFO)

    # Load configuration from file
    try:
        CONFIG = toml.load(os.path.join(sys.path[0], "config.toml"))
    except:
        # Exit if there is an error reading config file
        _LOGGER.exception("Error reading config.toml file. Exiting.")
        sys.exit(1)
    
    # Fill in any missing configuration variable with defaults
    for key in CONFIG_DEFAULTS:
        if key not in CONFIG: CONFIG[key] = CONFIG_DEFAULTS[key]
        for val in CONFIG_DEFAULTS[key]:
            if val not in CONFIG[key]: CONFIG[key][val] = CONFIG_DEFAULTS[key][val]

    # Set logging level (defaults to INFO)
    if CONFIG["general"]["log_level"] in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
        _LOGGER.setLevel(CONFIG["general"]["log_level"])

    # Pull out devices (if any) configured
    for d in CONFIG["devices"]:
        if "mac" in d: DEVICES[d["mac"]] = {}

    a = ATSensors(180, DEVICES)

    # Update sensor values in accordance with the REFRESH_INTERVAL set.
    first = True
    while True:
        # Get sensor data
        sensors = a.get_sensor_data()
        
        # Only connect to mqtt broker if we have data
        if sensors is not None:
            # Variable to store mqtt messages
            msgs = []
            
            # Send HA mqtt discovery messages to broker on first run
            if first:
                _LOGGER.info("Sending HA mqtt discovery configuration messages...")
                for mac, data in sensors.items():
                    
                    # Create device details for this device
                    device = {}
                    device["connections"] = [["mac", mac]]
                    if "serial_nr" in DEVICES[mac]: device["identifiers"] = [DEVICES[mac]["serial_nr"]]
                    if "manufacturer" in DEVICES[mac]: device["manufacturer"] = DEVICES[mac]["manufacturer"]
                    if "device_name" in DEVICES[mac]: device["name"] = DEVICES[mac]["device_name"]
                    if "model_nr" in DEVICES[mac]: device["model"] = DEVICES[mac]["model_nr"]

                    for name, val in data.items():
                        if name != "date_time":
                            try:
                                config = {}
                                s = next((item for item in CONFIG["devices"] if item["mac"] == mac), None)
                                if s != None:
                                    if name in s:
                                        config["name"] = s[name]["name"]
                                        if "device_class" in s[name] and s[name]["device_class"] is not None:
                                            config["device_class"] = s[name]["device_class"]
                                        if "icon" in s[name] and s[name]["icon"] is not None:
                                            config["icon"] = s[name]["icon"]
                                        if "unit_of_measurement" in s[name] and s[name]["unit_of_measurement"] is not None:
                                            config["unit_of_measurement"] = s[name]["unit_of_measurement"]
                                        config["uniq_id"] = mac+"_"+name
                                        config["state_topic"] = "airthings/"+mac+"/"+name
                                        config["device"] = device

                                msgs.append({'topic': "homeassistant/sensor/airthings_"+mac.replace(":","")+"/"+name+"/config", 'payload': json.dumps(config), 'retain': True})
                            except:
                                _LOGGER.exception("Failed while creating HA mqtt discovery messages.")
                
                # Publish the HA mqtt discovery data to mqtt broker
                mqtt_publish(msgs)
                _LOGGER.info("Done sending HA mqtt discovery configuration messages.")
                msgs = []
                time.sleep(5)
                first = False
            
            # Collect all of the sensor data
            _LOGGER.info("Collecting sensor value messages...")
            for mac, data in sensors.items():
                for name, val in data.items():
                    if name != "date_time":
                        if name == "temperature":
                            val = round(val,1)
                        else:
                            val = round(val)
                        _LOGGER.info("{} = {}".format("airthings/"+mac+"/"+name, val))
                        msgs.append({'topic': "airthings/"+mac+"/"+name, 'payload': val})
            
            # Publish the sensor data to mqtt broker
            mqtt_publish(msgs)
        else:
            _LOGGER.info("No sensor values collected.")

        # Wait for next refresh cycle
        _LOGGER.info("Waiting {} seconds.".format(CONFIG["general"]["refresh_interval"]))
        time.sleep(CONFIG["general"]["refresh_interval"])
