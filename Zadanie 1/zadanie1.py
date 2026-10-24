import random
import time
import requests

API_KEY = "LA2JCIVH1350IDNC"

while True:
    temperatura = random.randint(20, 30)
    print(f"Temperatura: {temperatura} °C")

    if temperatura > 28:
        print("Uwaga: temperatura przekroczyła 28 stopni Celsjusza")

    try:
        odpowiedz = requests.post("https://api.thingspeak.com/update",
            data={"api_key": API_KEY, "field1": temperatura},
            timeout=10
        )
        odpowiedz.raise_for_status()
    except requests.RequestException as blad:
        print("Błąd wysyłania:", blad)

    time.sleep(20)