import random
import time
import json
import paho.mqtt.client as mqtt

TEMAT = "iot/krzysztof_kata/dom_zadanie2"


def po_polaczeniu(client, userdata, flags, reason_code, properties):
    client.subscribe(TEMAT + "/polecenia")


def po_wiadomosci(client, userdata, message):
    polecenia = json.loads(message.payload.decode())

    if polecenia["lampa"] == 1:
        print("LAMPA: WŁĄCZONA")
    else:
        print("LAMPA: WYŁĄCZONA")

    if polecenia["klimatyzacja"] == 1:
        print("KLIMATYZACJA: WŁĄCZONA")
    else:
        print("KLIMATYZACJA: WYŁĄCZONA")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = po_polaczeniu
client.on_message = po_wiadomosci

client.connect("test.mosquitto.org", 1883)
client.loop_start()

obecnosc = int(input("Jesteś w domu? (1 = tak lub 0 = nie) "))

while True:
    dane = {
        "temperatura": random.randint(20, 32),
        "swiatlo": random.randint(0, 100),
        "obecnosc": obecnosc
    }

    print("\nPomiary:", dane)
    client.publish(TEMAT + "/pomiary", json.dumps(dane))

    time.sleep(20)