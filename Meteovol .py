import requests
import json
from datetime import datetime, timedelta

# CONFIGURATION

API_KEY = ""
JSON_LIEUX = "lieux.json"
DISCORD_WEBHOOK = ""
min_heures = 3

url = "https://api.weatherapi.com/v1/forecast.json"


# FONCTIONS

def direction_vent(deg):
    if deg < 22.5 or deg >= 337.5:
        return "nord"
    elif deg < 67.5:
        return "nord-est"
    elif deg < 112.5:
        return "est"
    elif deg < 157.5:
        return "sud-est"
    elif deg < 202.5:
        return "sud"
    elif deg < 247.5:
        return "sud-ouest"
    elif deg < 292.5:
        return "ouest"
    else:
        return "nord-ouest"


def creneaux_vol(voltab, min_heures):
    heures = sorted(voltab.keys())
    resultats = []

    debut = None
    longueur = 0

    for h in heures:

        if voltab[h] == "oui":
            if debut is None:
                debut = h
                longueur = 1
            else:
                longueur += 1

        else:
            if debut is not None and longueur >= min_heures:
                resultats.append((debut, h - 1, longueur))

            debut = None
            longueur = 0

    if debut is not None and longueur >= min_heures:
        resultats.append((debut, debut + longueur - 1, longueur))

    return resultats


def envoyer_discord(message):

    data = {
        "content": message
    }

    requests.post(DISCORD_WEBHOOK, json=data)


# LECTURE DU JSON

with open(JSON_LIEUX, "r", encoding="utf-8") as f:
    lieux = json.load(f)


demain = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

message_final = f"Analyse météo vol pour le {demain}\n\n"


# BOUCLE SUR LES LIEUX

for lieu in lieux:

    nom = lieu["nom"]
    ville = lieu["ville"]
    sens_vent = lieu["sens_vent"]

    params = {
        "key": API_KEY,
        "q": ville,
        "days": 2,
        "lang": "fr"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        message_final += f" {nom} : erreur API\n"
        continue

    data = response.json()

    voltab = {}

    for day in data["forecast"]["forecastday"]:

        if day["date"] == demain:

            for hour in day["hour"]:

                heure = int(hour["time"].split(" ")[1][:2])
                vent = hour["wind_kph"]
                orientation = hour["wind_degree"]
                pluie_mm = hour["precip_mm"]

                pluie = pluie_mm > 0

                pointcard = direction_vent(orientation)

                if not pluie and vent <= 25 and pointcard == sens_vent:
                    voltab[heure] = "oui"
                else:
                    voltab[heure] = "non"

    creneaux = creneaux_vol(voltab, min_heures)

    message_final += f" {nom} ({ville})\n"

    if creneaux:

        for debut, fin, duree in creneaux:
            message_final += f" {debut}h → {fin}h ({duree}h)\n"

    else:
        message_final += "X Aucun créneau\n"

    message_final += "\n"


# ENVOI DISCORD

envoyer_discord(message_final)
