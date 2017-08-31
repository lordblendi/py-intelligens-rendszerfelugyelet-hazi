#!/usr/bin/env python3
'''
Osszegyujti a szenzorokat a tavoli gepekrol
Hasznalat: ./getSensorData.py -m MACHINES -o OUTFILE [-n NAME]
MACHINES kotelezo, string tipusu
 a tavoli szamitogepek adatait tartalmazo CSV fajl eleresi utja
OUTFILE kotelezo, string tipusu
 a kimeneti fajl teljes eleresi utja
NAME opcionalis, kapcsolo
 bekapcsolasa eseten a szenzorok nevet is elhelyezi a kimenetben

@author     Szepes Nora
@created    2014-04-13

'''

import argparse, csv, re, sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from subprocess import Popen, PIPE

# wsman parancs meghivasat konnyito fuggveny
def call_wsman(Machine, Port, Protocol, User, Password, args):
    return Popen(['wsman','-h',Machine,'-u',User,'-P', Port,'-p',Password] + args, stdout=PIPE, stderr=PIPE).communicate()

# wsman kimenetebol generalunk stringet
def split_xmls(message):
    msg_list = []
    line_list = []
    for line in message.split('\n'):
        if line.startswith('<?xml'):
            if line_list:
                msg_list.append('\n'.join(line_list))
            line_list = []
        if line:
            line_list.append(line)
    if line_list:
        msg_list.append('\n'.join(line_list))
    return msg_list

#namespace kiszedese
#forras: http://stackoverflow.com/questions/9513540/python-elementtree-get-the-namespace-string-of-an-element
def namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''


#lekeri a parameterkent kapott gep szenzorait
#hozzadja oket a keszulo xml-hez
def do_it(Machine, Port, Protocol, User, Password):
 responseOut, responseErr = call_wsman(Machine, Port, Protocol, User, Password, ['enumerate', 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_Sensor'])

 #machine-enkent letrehozunk egy sensors subelementet
 sensors = SubElement(machinename, 'sensors') 	
 for msg in split_xmls(responseOut.decode('utf8'))[1:]:   
  responseXML = ET.fromstring(msg)
  #kiszedjuk a megfelelo CIM taget
  items = responseXML[1][0].find('{http://schemas.xmlsoap.org/ws/2004/09/enumeration}Items')
  if items is None:
   continue
  for sensor in items:
   #namespace kiszedese, hogy tudjunk vele szurni
   namespaceTag = namespace(sensor)
   #lekerjuk a deviceID-t es a name-t
   deviceID = sensor.find(namespaceTag + 'DeviceID').text
   name = sensor.find(namespaceTag + 'Name').text
   #ha van -n, akkor beleirjuk a name-t, ha nincs, akkor csak id lesz benne
   if name is None: name = ''
   if args.n: sensorXML = SubElement(sensors, 'sensor', {'id':deviceID, 'name':name})
   else: sensorXML = SubElement(sensors, 'sensor', {'id':deviceID})

if __name__ == '__main__':
 parser = argparse.ArgumentParser(prog='getSensorData.py',add_help=False)
 parser.add_argument('-m', metavar='MACHINES', required=True)
 parser.add_argument('-o', metavar='OUTFILE', required=True)
 parser.add_argument('-n', action='store_true')
 
 args = parser.parse_args()
 
 #letrehozzuk a sensordata elementet
 sensordata = Element('sensordata')
 with open(args.m, 'r') as f:
  #beolvassuk a paramterekent kapott csv sorait
  for line in csv.DictReader(f):
    Machine,Port,Protocol,User,Password = (line['machineName'], line['port'],line['protocol'],line['user'],line['password'])
    print("Szerver:",Machine)
     
    #hiba ellenorzes, hogy elerheto-e a kapott ip-rol a gep      
    out, error = call_wsman(Machine,Port,Protocol,User,Password,['identify'])             
    if len(error) > 0:
     print('Csatlakozasi hiba: ', Machine)
     continue

    #xml keszites
    #csv soraikent kell machinename, igy azt a feldolgozo fgv elott letrehozzuk
    machinename = SubElement(sensordata, 'machine', {'name':Machine})
    do_it(Machine,Port,Protocol,User,Password)
 
 #ET.dump(sensordata)
 #kiirjuk az egeszet a parameterkent kapott fajlba xmlkent
 ET.ElementTree(sensordata).write(args.o, encoding="utf-8", xml_declaration=True)