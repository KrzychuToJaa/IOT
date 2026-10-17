import json
import requests
import paho.mqtt.client as mqtt

API_KEY = "8D1ZZJWZMM2XMVTU"
TEMAT = "iot/krzysztof_kata/dom_zadanie2"


def po_polaczeniu(client, userdata, flags, reason_code, properties):
    client.subscribe(TEMAT + "/pomiary")
    print("Sterownik gotowy")


def po_wiadomosci(client, userdata, message):
    dane = json.loads(message.payload.decode())

    temperatura = dane["temperatura"]
    swiatlo = dane["swiatlo"]
    obecnosc = dane["obecnosc"]

    if swiatlo < 30:
        lampa = 1
    else:
        lampa = 0

    if temperatura > 28 and obecnosc == 1:
        klimatyzacja = 1
    else:
        klimatyzacja = 0

    polecenia = {
        "lampa": lampa,
        "klimatyzacja": klimatyzacja
    }

    client.publish(TEMAT + "/polecenia", json.dumps(polecenia))

    print("\nOdebrano:", dane)
    print("Wysłano polecenia:", polecenia)

    odpowiedz = requests.post(
        "https://api.thingspeak.com/update",
        data={
            "api_key": API_KEY,
            "field1": temperatura,
            "field2": swiatlo,
            "field3": obecnosc,
            "field4": lampa,
            "field5": klimatyzacja
        },
        timeout=10
    )

    print("Odpowiedź ThingSpeak:", odpowiedz.text)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = po_polaczeniu
client.on_message = po_wiadomosci

client.connect("test.mosquitto.org", 1883)
client.loop_forever()