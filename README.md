Domoticz Plugin ThesslaGreen recuperators with RS485 modbus interface
https://thesslagreen.com/

Plugin should work with all AirPack family models, however was tested only with AirPack4 500h
supported functionality - 
reading temperature: outside, supply, exhaust , fpx, duct_supply, gwc, ambient
reading AirFlow: supply and exhaust
Possibility to turn on/off,  read/set special flow mode.


Installation:
cd ~/domoticz/plugins
git clone https://github.com/voyo/DDS-238-7-Modbus


Used python modules:
pyserial -> -https://pythonhosted.org/pyserial/
minimalmodbus -> http://minimalmodbus.readthedocs.io

Restart your domoticz server.
