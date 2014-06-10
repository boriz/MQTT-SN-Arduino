MQTT-SN-Arduino
===============

TODO: I don't like the repo name anymore, change it to something more generic

Connecting mesh network to the MQTT broker and tunneling MQTT protocol over Websocket.
--------------

Mesh network is based on the open-source MeshBee modules with Arduino end devices and Raspberry Pi acting as MQTT mesh network gateway.
TODO: Add links to MQTT, etc

Overall project architecture:
TODO: Awesome diagrams should be here

There are multiple pieces of the puzzle:
- Arduino/libraries/mqttsn/folder. This is an MQTT-SN Arduino library, fork of theh http://bitbucket.org/MerseyViking/mqtt-sn-arduino with some minor bug fixes (TODO: get in touch with the repo owner to merge). Copy mqttsn folder into your Arduino libraries folder.
- Arduino/MqttsnClient folder is an Arduino test sketch (publishes Arduino temperature to /arduino/temp topic). There is no frame logic, for now assuming direct/transparent serial connection to the broker.
- "serial-mqtts" folder. Serial to MQTT-SN/UDP gateway. Dummy simple Python script to read MQTT-SN from serial port and send it as UDP packet.
- RSMB Broker. Compiled version and configuration file of the "Really Small Message Broker" from  http://git.eclipse.org/c/mosquitto/org.eclipse.mosquitto.rsmb.git
- Websocket to TCP gateway. This is slightly modified "websockify" project from https://github.com/kanaka/websockify to tunnel MQTT over Websocket. Compatible with http://mqtt.io client.

TODO: 
  1. Test! 
  2. Create PLC MQTT client.
