Domoticz Plugin ThesslaGreen recuperators with RS485 modbus interface<br>
https://thesslagreen.com/

Plugin should work with all AirPack family models, however was tested only with AirPack4 500h

supported functionality - <br>
reading temperature: outside, supply, exhaust , fpx, duct_supply, gwc, ambient<br>
reading AirFlow: supply and exhaust

Possibility to turn on/off,  read/set special flow mode.


Installation:<br>
cd ~/domoticz/plugins<br>
git clone https://github.com/voyo/ThesslaGreen-modbus
<br>

Used python modules:<br>
pyserial -> -https://pythonhosted.org/pyserial/ <br>
minimalmodbus -> http://minimalmodbus.readthedocs.io <br>
<br>
Restart your domoticz server.
