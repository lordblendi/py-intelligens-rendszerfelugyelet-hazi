# Intelligens rendszerfelügyelet Python házi

Ezt a Python házit a Intelligens rendszerfelügyelet tantárgyhoz készítettem a BME-s tanulmányaim során a 2013/2014/2 félévben.

## Feladat

Az egyetemi cloud rendszer szervertermében a szerverek működéséhez szükséges fizikai alapfeltételeksérülnek (újabbanleginkább a klíma gyakori meghibásodása miatt). Mint rendszermérnök, ránk bízták a feladatot, hogy agépek monitorozását segítsük. Első ötletünk, hogy aszervertermigépek fizikai jellemzőit mérő szenzorok listáját kigyűjtsük, így tudjuk, hogy később milyen adatokat lesz érdemes figyelni.A gépeken  különböző operációs rendszerek futhatnak (Linux, Windows vagy ESXi), de szerencsére mindegyik platform támogatja a CIM szabványt, így van esélyünk a feladat megoldására

.Készítsünk tehát egy ***Python 3*** szkriptet, ami ***WS-Management*** protokollt használvaösszegyűjti a szenzorokat a távoli gépekről.

### A szkript elnevezése és paraméterezése

```pyython
getSensorData.py -m MACHINES -o OUTFILE [-n]
```
A szkriptnek kötelező ezt az elnevezést és paraméterezést használnia. A szkript használjon nevesített paramétereket. A paraméterek sorrendje ne legyen megkötve.

A szkripta paramétereket a következő formában fogadja:

  - MACHINES: a távoli számítógépek adatait tartalmazó CSV fájlelérési útja(kötelező, string típusú).
  - OUTFILE: a kimeneti fájl teljes elérési útja (kötelező, string típusú).
  - NAME: bekapcsolása esetén a szenzorok nevét is helyezze el a kimenetben (opcionális, kapcsoló).

Példa a szkript lehetséges használataira:

```python
getSensorData.py -m machines.csv -o physicalsensors.xml
```

```python
getSensorData.py -o /tmp/sensors.xml -n -m computers.csv
```

### Bemeneti fájl
A bemeneti fájl egy egyszerű CSV fájl:

```csv
machineName,port,protocol,user,password
192.168.250.128,5985,http,administrator,password
server01,5986,https,meres,password2
```

(A jelszó nyílt szövegben tárolása éles környezetben nem javasolt megoldás, ez most csak a házi feladat egyszerűsége miatt engedhető meg. Éles környezetben a jelszót érdemes ilyenkor például titkosítva tárolnivagy nyilvános kulcsú titkosításra alapuló módszereket alkalmazni.)

### Kimenet

A szkript kimenete egy UTF-8 kódolású XMLfájl a következő formában:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sensordata>
  <machine name="server01">
    <sensors><sensor id="FAN1" name=""/><sensor id="FAN2" name=""/></sensors>
  </machine>
  <machine name="192.168.1.1"><sensors/></machine>
</sensordata>A kimenet tehát a szenzorokat gépenkéntgyűjti össze. A kimenetnek az alábbi XML Schema-ra kell illeszkednie:<xs:schema attributeFormDefault="unqualified" elementFormDefault="qualified" xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="sensordata">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="machine" maxOccurs="unbounded" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="sensors">
                <xs:complexType mixed="true">
                  <xs:sequence>
                    <xs:element name="sensor" maxOccurs="unbounded" minOccurs="0">
                      <xs:complexType>
                        <xs:simpleContent>
                          <xs:extension base="xs:string"><xs:attribute type="xs:string" name="id" use="required"/><xs:attribute type="xs:string" name="name" use="optional"/></xs:extension>
                        </xs:simpleContent>
                      </xs:complexType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:sequence><xs:attribute type="xs:string" name="name" use="required"/></xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```

### További elvárások

A szkript kezelje azt az esetet, ha a távoli géphez nem sikerül csatlakozni. Ilyenkor írjon ki a konzolos kimenetrehibát,ne kerüljön be az adott gép az XML-fájlba,és folytassa a többi gép feldolgozását.


## Megjegyzések

Az alkalmazás használja a Python ElementTree XML Apiját, így ha az még nincs telepítva a gépen, akkor ezzel a paranccsal lehet telepíteni:
```bash
sudo zypper install python3-xml
```

Futtatási jogot így adhatunk:
```bash
chmod +x getSensorData.py
```

Ha a fájlt Windowson hozzuk létre és drag'n'dropoltuk, akkor dos2unix-ot is telepíteni kell, hogy futtatni tudjuk:
```bash
sudo zypper install dos2unix
```

Feltételezem, hogy a paraméterként kapott .csv fájl (-m paraméternél) létezik, és a feladatkiírásnak megfelel.

Valamint feltételezem, hogy a -o paramétereként megadott kimeneti fájl nem írásvédett.

A feladat megoldásához először elindtottam az sfcb-t, és a yawnt, hogy megnézzem firefoxban az elvárt értékeket:
```bash
sudo systemctl start sfcb.service
yawn
```

Az openwsman elindításához a következő:
```bash
sudo systemctl start openwsman
```
parancsot használtam, és először parancssorban próbáltam meg lekérni adatokat belőle.

Görgethető változat megnyitásához parancssorban ezt kell használni:
``` bash
wsman -h localhost -u meres -p LaborImage enumerate 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_Sensor' | less
```

## Tesztelés

Tesztesetek:

- test1: program működése, -n kapcsolóval.
- test2: előző teszt eredményének felülírása működik, paraméterek felcserélése, -n kivétele
- test3: paraméterek kihagyása
- test4: -m paramétere nem létezik
- test5: generálunk egy test3.xml-t, majd azt írásvédetté tesszük, végül megpróbáljuk megint felülírni

Az elvárt működések:

- Miután a localhos és a 127.0.0.1 ugyanoda mutatnak, így azoknak az eredményeknek egyezniük kell.
- A server01 mindig csatlakozási hibát kell, hogy generáljon.
