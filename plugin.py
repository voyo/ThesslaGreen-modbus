#!/usr/bin/env python
"""
ThesslaGreen recuperator. Domoticz plugin.
https://thesslagreen.com/
Author: Wojtek Sawasciuk  <voyo@no-ip.pl>

Requirements: 
    1.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    2.Communication module Modbus USB to RS485 converter module
"""
"""
<plugin key="ThesslaGreen" name="ThesslaGreen-Modbus" version="0.1" author="voyo@no-ip.pl">
    <params>
        <param field="SerialPort" label="Modbus Port" width="200px" required="true" default="/dev/ttyUSB0" />
        <param field="Mode1" label="Baud rate" width="40px" required="true" default="9600"  />
        <param field="Mode2" label="Device ID" width="40px" required="true" default="1" />
        <param field="Mode3" label="Reading Interval min." width="40px" required="true" default="1" />
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="false" />
            </options>
        </param>
    </params>
</plugin>

"""

import minimalmodbus
import serial
import Domoticz





class Switch:
   def __init__(self,ID,name,register,functioncode: int = 3,options=None, Used: int = 1):
        self.ID = ID
        self.name = name
#        self.type = type
#        self.Type = Type
#        self.Subtype = Subtype
#        self.Switchtype=Switchtype
        self.register = register
        self.functioncode = functioncode
        self.Used=Used
        self.nod = 0
        self.value = 0
        self.options = options if options is not None else None        
        if self.ID not in Devices:
             msg = "Registering device: "+self.name+" "+str(self.ID)
             Domoticz.Log(msg)        
             Domoticz.Device(Name=self.name, Unit=self.ID, Type=244, Subtype=62, Switchtype=18,Used=self.Used,Options=self.options).Create()


   def LevelValueConversion2Data(self,level):
        if self.register==4208:
                value = (level / 10) - 1
        if self.register==4224:
                if level == 0:
                  value = 0 # off
                elif level==10:
                  value = 0 # off
                elif level==20:
                  value = 1 # okap
                elif level==30:
                  value = 2 # kominek
                elif level==40:
                  value = 3 # WIETRZENIE (prze??. dzwonkowy)
                elif level==50:
                  value = 4 # WIETRZENIE (prze????cznik ON/OFF)
                elif level==60:
                    value = 5 # H2O/WIETRZENIE (higrostat)
                elif level==70:
                    value = 6 # JP/WIETRZENIE (cz. jako??ci pow.)
                elif level==80:
                    value = 7 # WIETRZENIE (aktywacja r??czna)
                elif level==90:
                    value = 8 # WIETRZENIE (tryb AUTOMATYCZNY)
                elif level==100:
                    value = 9 # WIETRZENIE (tryb MANUALNY)
                elif level==110:
                    value = 10 # OTWARTE OKNA
                elif level==120:
                    value = 11 # PUSTY DOM
                else:
                    Domoticz.Log("Level value conversion - data not valid level:"+str(level)+" register:"+str(self.register))    
        if Parameters["Mode6"] == 'Debug':                    
               Domoticz.Log("Conversion mapping from "+str(level)+" to "+str(value))
        return value


   def LevelValueConversion2Level(self,data):
        if self.register==4387:
                value = data
        if self.register==4208:
                value = (data +1 ) * 10
        if self.register==4224: 
                if data == 0:
                  value = 10 # wylaczone
                elif data==1:
                  value = 20 # okap
                elif data==2:
                  value = 30 # kominek
                elif data==3:
                  value = 40 # WIETRZENIE (prze??. dzwonkowy)
                elif data==4:
                    value = 50 # WIETRZENIE (prze????cznik ON/OFF)
                elif data==5:
                    value = 60 # H2O/WIETRZENIE (higrostat)
                elif data==6:
                    value = 70 # JP/WIETRZENIE (cz. jako??ci pow.)
                elif data==7:
                    value = 80 # WIETRZENIE (aktywacja r??czna)
                elif data==8:
                    value = 90 # WIETRZENIE (tryb AUTOMATYCZNY)    
                elif data==9:
                    value = 100 # WIETRZENIE (tryb MANUALNY)
                elif data==10:
                    value = 110 # OTWARTE OKNA
                elif data==11:
                    value = 120 # PUSTY DOM        
                else:
                    Domoticz.Log("Level value conversion - data not valid:"+str(data)+"register:"+self.register)    
        if Parameters["Mode6"] == 'Debug':                    
               Domoticz.Log("Conversion mapping from "+str(data)+" to "+str(value))
        return value


   def UpdateValue(self,RS485):
        if self.functioncode == 3 or self.functioncode == 4:
                     payload = RS485.read_register(self.register,number_of_decimals=self.nod,functioncode=self.functioncode)
        data = payload
# 	for devices with 'level' we need to do conversion on domoticz levels, like 0->10, 1->20, 2->30 etc        
        value = self.LevelValueConversion2Level(data)
        self.value = value
        Devices[self.ID].Update(0,str(value),True)  # force update, even if the value has no changed.
        if Parameters["Mode6"] == 'Debug':
                 Domoticz.Log("Updating switch: "+self.name+"wartosc z rejestru: "+str(data) + " , wartosc levelu: "+str(value))                 


   def UpdateRegister(self,RS485,command,level):
        value = self.LevelValueConversion2Data(level)
        if Parameters["Mode6"] == 'Debug':
                Domoticz.Log("updating register:"+str(self.register)+" with value: "+str(value))
        try:
            RS485.write_register(self.register,value)
        except Exception as e:
            Domoticz.Log("Connection failure: "+str(e));    
#        write_register(registeraddress: int, value: Union[int, float], number_of_decimals: int = 0, functioncode: int = 16, signed: bool = False) → None[source]



class Dev:
    def __init__(self,ID,name,nod,register,functioncode: int = 3,options=None, Used: int = 1, signed: bool = False, Description=None, TypeName=None,Type: int = 0, SubType:int = 0 , SwitchType:int = 0  ):
        self.ID = ID
        self.name = name
        self.TypeName = TypeName if TypeName is not None else ""
        self.Type = Type
        self.SubType = SubType
        self.SwitchType = SwitchType
        self.nod = nod
        self.value = 0
        self.signed = signed        
        self.register = register
        self.functioncode = functioncode
        self.options = options if options is not None else None
        self.Used=Used
        self.Description = Description if Description is not None else ""
        if self.ID not in Devices:
            msg = "Registering device: "+self.name+" "+str(self.ID)+" "+self.TypeName+"  Description: "+str(self.Description);
            Domoticz.Log(msg)        
            if self.TypeName != "":
                 Domoticz.Log("adding Dev with TypeName, "+self.TypeName)
                 Domoticz.Device(Name=self.name, Unit=self.ID, TypeName=self.TypeName,Used=self.Used,Options=self.options,Description=self.Description).Create()
            else:
                 Domoticz.Device(Name=self.name, Unit=self.ID,Type=self.Type, Subtype=self.SubType, Switchtype=self.SwitchType, Used=self.Used,Options=self.options,Description=self.Description).Create()
                 Domoticz.Log("adding Dev with Type, "+str(self.Type))
                      


    def UpdateValue(self,RS485):
                 if self.functioncode == 3 or self.functioncode == 4:
                     payload = RS485.read_register(self.register,number_of_decimals=self.nod,functioncode=self.functioncode,signed=self.signed)
                 data = payload
                 Devices[self.ID].Update(0,str(data)+';0',True) # force update, even if the voltage has no changed. 
                 if Parameters["Mode6"] == 'Debug':
                     Domoticz.Log("Device:"+self.name+" data="+str(data)+" from register: "+str(hex(self.register)) )                 
                    


class BasePlugin:
    def __init__(self):
        self.runInterval = 1
        self.RS485 = ""
        return

    def onStart(self):
        self.RS485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(Parameters["Mode2"]))
        self.RS485.serial.baudrate = Parameters["Mode1"]
        self.RS485.serial.bytesize = 8
        self.RS485.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.RS485.serial.stopbits = 1
        self.RS485.serial.timeout = 1
        self.RS485.debug = False
        self.RS485.mode = minimalmodbus.MODE_RTU
        
        devicecreated = []
        Domoticz.Log("ThesslaGreen-Modbus plugin start")

        self.sensors = [
                 Dev(1,"outside_temp",1,16,functioncode=4,TypeName="Temperature",Description="Outside temperature",signed=True),
                 Dev(2,"supply_temp",1,17,functioncode=4,TypeName="Temperature",Description="Supply temperature",signed=True),
                 Dev(3,"exhaust_temp",1,18,functioncode=4,TypeName="Temperature",Description="Exhaust temperature",signed=True),
                 Dev(4,"fpx_temp",1,19,functioncode=4,TypeName="Temperature",signed=True),
                 Dev(5,"duct_supply_temp",1,20,functioncode=4,Used=0,TypeName="Temperature",signed=True),
                 Dev(6,"gwc_temp",1,21,functioncode=4,Used=0,TypeName="Temperature",signed=True),
                 Dev(7,"ambient_temp",1,22,functioncode=4,TypeName="Temperature",signed=True),
                 Dev(8,"supplyAirFlow",0,256,functioncode=3,Type=243,SubType=30),
                 Dev(9,"exhaustAirFlow",0,257,functioncode=3,Type=243,SubType=30)

            ]
        self.settings = [
                 Switch(51,"onOffPanelMode",4387,functioncode=3),
                 Switch(52,"mode",4208,functioncode=3,options={"LevelActions": "|act1| |act2|","LevelNames": "|" + "Manual" + "|" + "Automatic" + "|" + "Temporary", "LevelOffHidden": "true", "SelectorStyle": "0"}),
#0 - brak  1 - OKAP  2 - KOMINEK	3 - WIETRZENIE (prze??. dzwonkowy)	4 - WIETRZENIE (prze????cznik ON/OFF)	5 - H2O/WIETRZENIE (higrostat) 6 - JP/WIETRZENIE (cz. jako??ci pow.)
#7 - WIETRZENIE (aktywacja r??czna)	8 - WIETRZENIE (tryb AUTOMATYCZNY)	9 - WIETRZENIE (tryb MANUALNY) 	10 - OTWARTE OKNA	11 - PUSTY DOM
                 Switch(53,"specialMode",4224,functioncode=3,options={"LevelActions": "|act1| |act2|","LevelNames": "|" + "Wylaczone" + "|" + "Okap" + "|" + "Kominek" + "|" + "WIETRZENIE (przel. dzwonkowy)" + "|" + "WIETRZENIE (przel. on/off)" + 
                 "|" + "H2O/Wietrzenie (higrostat)" +"|"+ "JP/Wietrzenie (cz.jakosci pow.)" + "|" + "WIETRZENIE (aktywacja reczna)" + "|" + "WIETRZENIE (tryb AUTOMATYCZNY)" + "|" + "WIETRZENIE (tryb MANUALNY)" + "|" + "OTWARTE OKNA" +
                 "|" + "PUSTY DOM"
                  , "LevelOffHidden": "false", "SelectorStyle": "1"})
                  ]


    def onStop(self):
        Domoticz.Log("ThesslaGreen Modbus plugin stop")

    def onHeartbeat(self):
        self.runInterval -=1;
        if self.runInterval <= 0:
            for i in self.sensors:
                try:
                         # Get data from modbus
                        Domoticz.Log("Getting data from modbus for device:"+i.name+" ID:"+str(i.ID))
                        self.sensors[i.ID-1].UpdateValue(self.RS485)
                except Exception as e:
                        Domoticz.Log("Connection failure: "+str(e));
                else:
                        if Parameters["Mode6"] == 'Debug':
                            Domoticz.Log("in HeartBeat "+i.name+": "+format(i.value))
            self.runInterval = int(Parameters["Mode3"])

            for i in self.settings:
                l = len(self.settings)
                dev_len=len(self.sensors)
                try:
                         # Get data from modbus
                        Domoticz.Log("Getting data from modbus for device:"+i.name+" ID:"+str(i.ID))
                        self.settings[i.ID-1-50].UpdateValue(self.RS485)
                except Exception as e:
                        Domoticz.Log("Connection failure: "+str(e));
                else:
                        if Parameters["Mode6"] == 'Debug':
                            Domoticz.Log("in HeartBeat "+i.name+": "+format(i.value))
            self.runInterval = int(Parameters["Mode3"]) 



    def onCommand(self, u, Command, Level, Hue):
        if Parameters["Mode6"] == 'Debug':
                Domoticz.Log(str(Devices[u].Name) + ": onCommand called: Parameter '" + str(Command) + "', Level: " + str(Level))
        dev_len=len(self.sensors)
        try:
            self.settings[u-1-50].UpdateRegister(self.RS485,Command,Level)
        except Exception as e:
            Domoticz.Log("Connection failure: "+str(e));
    


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onHeartbeat():
    global _plugin
    Domoticz.Log("onHeartbeat called")
    _plugin.onHeartbeat()


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    Domoticz.Log("onCommand called")
    _plugin.onCommand(Unit, Command, Level, Hue)

   

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Log("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Log("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Log("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Log("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Log("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Log("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Log("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Log("Device LastLevel: " + str(Devices[x].LastLevel))
    return
