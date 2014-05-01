import paho.mqtt.client as mosquitto

def on_connect(mosq, obj, rc):
#    mosq.subscribe("arduino/temp", 0)
    print("Connect. rc: "+str(rc))

def on_message(mosq, obj, msg):
    print("Message. Top:"+msg.topic+"; Qos:"+str(msg.qos)+"; Payload:"+str(msg.payload))

def on_publish(mosq, obj, mid):
    print("Publish. Mid: "+str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: Mid:"+str(mid)+"; Qos:"+str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

# If you want to use a specific client id, use
# mqttc = mosquitto.Mosquitto("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
mqttc.on_log = on_log

mqttc.connect("192.168.1.10", 1883, 60)
#mqttc.connect("127.0.0.1", 1883, 60)

mqttc.subscribe("#", 0)
#mqttc.subscribe(("tuple", 1))
#mqttc.subscribe([("list0", 0), ("list1", 1)])

mqttc.loop_forever()