# FHEM Python Binding (BETA)

FHEM Python binding allows the usage of Python 3 (NOT 2!) language to write FHEM modules

This repository includes following working modules:
Module | Description
-------|--------------
[ble_presence](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/ble_presence/README.md)|Presence detection incl. RSSI for Bluetooth Low Energy
[ble_reset](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/ble_reset/README.md)|Resets all Bluetooth interfaces every X hours
[bt_presence](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/bt_presence/README.md)|Presence detection incl. RSSI for Bluetooth
discover_mdns|Discover mDNS devices
discover_ble|Discover Bluetooth LE devices
discover_upnp|Discover UPnP devices
dlna_dmr|Control DLNA MediaRenderer devices)
[eq3bt](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/eq3bt/README.md)|Control EQ3 Bluetooth thermostat
[esphome](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/esphome/README.md)|Installs and starts the ESP Home dashboard for easy ESP Home device management
googlecast|Control Cast devices
helloworld|Hello World example
[miflora](https://github.com/dominikkarall/fhem_pythonbinding/tree/master/FHEM/bindings/python/lib/miflora/README.md)|Xiaomi BLE Plant Sensor
[miio](https://github.com/dominikkarall/fhem_pythonbinding/tree/master/FHEM/bindings/python/lib/miio/README.md)|Control Xiaomi WiFi devices
[mitemp](https://github.com/dominikkarall/fhem_pythonbinding/tree/master/FHEM/bindings/python/lib/mitemp/README.md)|Xiaomi BLE Temperature/Humidity Sensor
[nespresso_ble](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/nespresso_ble/README.md)|Nespresso Bluetooth coffee machine
[object_detection](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/object_detection/README.md)|TensorFlow Lite object detection
[ring](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/ring/README.md)|Ring doorbell/chime/cam
[wienerlinien](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/wienerlinien/README.md)|Wiener Linien departure times
xiaomi_gateway3|Xiaomi Gateway V3 (only V3!)
[xiaomi_tokens](https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/xiaomi_tokens/README.md)|Retrieve all Xiaomi Tokens from Cloud

## Installation
Python >=3.7 is required, Python 2 won't work!

### Console
```
sudo apt install python3 python3-pip

sudo cpan Protocol::WebSocket

sudo pip3 install asyncio websockets importlib_metadata
```
### FHEM
```
update add https://raw.githubusercontent.com/dominikkarall/fhem_pythonbinding/master/controls_pythonbinding.txt

update

define local_pybinding BindingsIo Python
```

All further requirements are installed automatically via pip as soon as the specific module is used the first time.
 
## Usage in FHEM
 - `define castdevice PythonModule googlecast "Living Room"`
 - `define eq3bt PythonModule eq3bt 00:11:22:33:44:66:77`
 - `define upnp PythonModule discover_upnp`

## Run Python modules on remote Python peers (e.g. extend Bluetooth range)
FHEM Pythonbinding allows to run modules locally (same device as FHEM runs on) or on remote peers. Those remote peers only make sense if you want to extend the range of bluetooth or want to distribute the load of some modules to other more powerfull devices (e.g. video object detection).

The following steps are only needed if you want to install FHEM Pythonbinding on a remote peer, you should not run them on your FHEM installation.

- Follow installation steps (only Console) above on remote device
- `git clone https://github.com/dominikkarall/fhem_pythonbinding.git`
- Systemd configuration
  - change fhem_pythonbinding/fhem_pythonbinding.service acording to your system
  - `sudo cp fhem_pythonbinding/fhem_pythonbinding.service /etc/systemd/system/`
  - `sudo systemctl daemon-reload`
  - `sudo systemctl enable fhem_pythonbinding`
  - `sudo systemctl start fhem_pythonbinding`
- FHEM configuration
  - `define remote_pybinding BindingsIo IP:15733 Python`
  - `define eq3device PythonModule eq3bt MAC`
  - `attr eq3device IODev remote_pybinding`

## Functionality

### 10_BindingsIo
This module is a DevIo device which builds a language neutral communicaton bridge in JSON via websockets.
### 10_PythonBinding
This module just starts the fhem_pythonbinding server instance
### 10_PythonModule
This module is used as the bridge to BindingsIo. It calls BindingsIo with IOWrite.
### fhem_pythonbinding
This is the Python server instance which handles JSON websocket messages from BindingsIo. Based on the message it executes the proper function and replies to BindingsIo via websocket.

### Call flow
This example shows how Define function is called from the Python module.
 1. define castdevice PythonModule googlecast "Living Room"
 2. PythonModule sends IOWrite to BindingsIo
 3. BindingsIo sends a JSON websocket message to fhem_pythonbinding
 4. fhem_pythonbinding loads the corresponding module (e.g. googlecast), creates an instance of the object (e.g. googlecast) and calls the Define function on that instance
 5. Define function is executed within the Python context, as long as the function is executed, FHEM waits for the answer the same way as it does for Perl modules
 6. Python Define returns the result via JSON via websocket to BindingsIo

At any time within the functions FHEM functons like readingsSingleUpdate(...) can be called by using the fhem.py module (fhem.readingsSingleUpdate(...)). There are just a few functions supported at the moment.

![Flow Chart](/flowchart.png)

## Write your own module
Check helloworld example for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use run_in_executor (see googlecast code).
