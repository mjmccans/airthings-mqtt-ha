## [1.2.0] - 2022-08-05

### BREAKING CHANGES
* Changed bluetooth library from bluepy to bleak, a more modern bluetooth library. This change has material
benefits because bleak communicates with the bluetooth adapter via dbus and does not require additional permissions.

### NEW
* Firmware version displayed on device details page.

## [1.1.0] - 2022-05-05
### Breaking Changes
* Configuration file format has been changed from `toml` to `json` for better consistency with the add-on version of this script.

### New
* Command line option `--generate_config` added to automatically generate a suggested configuration file.
* Support for battery and illuminance sensors for Airthings Wave+ devices pulled from upstream.
* Add support for long-term statistics.
* New configuration option to retain your sensor values in the MQTT broker.

### Fixes
* Reconcile the addon and non-addon code bases to allow easier future development.


