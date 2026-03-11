#  Météo Vol Parapente — Alertes Discord

> Script Python qui analyse les conditions météo pour le **parapente** et envoie un résumé quotidien sur Discord, automatisé chaque matin à 8h via **n8n**.

---

##  Description

Ce script interroge l'API [WeatherAPI](https://www.weatherapi.com/) pour chaque site de vol configuré, évalue les conditions météo heure par heure pour le lendemain, et identifie les **créneaux de vol favorables** selon trois critères :

-  Pas de précipitations
-  Vent ≤ 25 km/h
-  Direction du vent compatible avec le site (décollage face au vent)

Le résultat est envoyé automatiquement dans un **salon Discord** via webhook, tous les jours à 8h grâce à un workflow **n8n** hébergé sur Raspberry Pi.

---

##  Exemple de message Discord

```
Analyse météo vol pour le 2025-08-15

 Col de la Forclaz (Talloires)
 9h → 12h (4h)
 15h → 17h (3h)

 Saint-Hilaire du Touvet (Saint-Hilaire-du-Touvet)
X Aucun créneau

 Chabre (Laragne-Montéglin)
 10h → 14h (5h)
```

---

## ⚙️ Configuration

### API WeatherAPI

1. Créer un compte gratuit sur [weatherapi.com](https://www.weatherapi.com/)
2. Copier la clé API depuis le tableau de bord
3. La coller dans `meteo_vol.py` :

```python
API_KEY = "votre_clé_api_ici"
```

### Webhook Discord

1. Dans votre serveur Discord : **Paramètres du salon → Intégrations → Webhooks → Nouveau webhook**
2. Copier l'URL du webhook
3. La coller dans `meteo_vol.py` :

```python
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."
```

### Sites de vol — `lieux.json`

Modifier le fichier `lieux.json` pour configurer vos sites. Chaque entrée contient trois champs :

```json
[
  {
    "nom": "Nom affiché dans le message Discord",
    "ville": "Ville ou coordonnées GPS pour l'API météo",
    "sens_vent": "nord"
  }
]
```

#### Valeurs acceptées pour `sens_vent`

Il s'agit de la direction **d'où vient le vent** favorable au décollage du site.

| Valeur | Description |
|--------|-------------|
| `nord` | Vent soufflant du nord |
| `nord-est` | Vent soufflant du nord-est |
| `est` | Vent soufflant de l'est |
| `sud-est` | Vent soufflant du sud-est |
| `sud` | Vent soufflant du sud |
| `sud-ouest` | Vent soufflant du sud-ouest |
| `ouest` | Vent soufflant de l'ouest |
| `nord-ouest` | Vent soufflant du nord-ouest |

>  Pour `ville`, vous pouvez utiliser un nom de ville, un code postal, ou des coordonnées GPS au format `"45.8566,6.3522"`.

### Durée minimale d'un créneau

Modifier `min_heures` dans `meteo_vol.py` (défaut : 3 heures) :

```python
min_heures = 3
```

---

##  Automatisation avec n8n

Le script est déclenché automatiquement **chaque jour à 8h00** via un workflow [n8n](https://n8n.io/) auto-hébergé sur Raspberry Pi.

### Structure du workflow

```
Schedule Trigger (8h00 chaque jour)
  └─→ Execute Command
        └─→ python3 /home/pi/meteo-vol-discord/meteovol.py
```

### Mise en place

1. Dans l'interface n8n, créer un nouveau workflow
2. Ajouter un nœud **Schedule Trigger** :
   - Mode : `Cron`
   - Expression cron : `0 8 * * *`
3. Ajouter un nœud **Execute Command** :
   - Command : `python3 /home/pi/meteo-vol-discord/meteo_vol.py`
4. Connecter les deux nœuds, sauvegarder et **activer** le workflow

> Le script se charge lui-même d'envoyer le message sur Discord — n8n ne fait que le déclencher chaque matin.

---

##  Structure du projet

```
meteo-vol-discord/
├── meteo_vol.py        # Script principal
├── lieux.json          # Configuration des sites de vol
└── README.md
```

---

##  Personnalisation

| Paramètre | Emplacement | Description |
|-----------|-------------|-------------|
| `API_KEY` | `meteo_vol.py` | Clé API WeatherAPI |
| `DISCORD_WEBHOOK` | `meteo_vol.py` | URL du webhook Discord |
| `min_heures` | `meteo_vol.py` | Durée minimale d'un créneau (heures) |
| Sites de vol | `lieux.json` | Nom, ville et orientation des sites |

---

##  Améliorations possibles

### Robustesse et gestion des erreurs

- Ajouter un **timeout** sur les appels API pour éviter que le script reste bloqué en cas de problème réseau
- Gérer les **erreurs HTTP** (quota dépassé, clé invalide, site introuvable) avec un message explicite dans Discord plutôt qu'un crash silencieux
- Valider le fichier `lieux.json` au démarrage et signaler les entrées mal formées
- Logger les erreurs dans un fichier pour faciliter le débogage depuis n8n

### Enrichissement des données météo parapente

- **Rafales de vent** — le vent moyen peut être acceptable alors que les rafales sont rédhibitoires ; ajouter un seuil sur `gust_kph`
- **Hauteur de la base des nuages** — essentielle pour évaluer si le plafond est suffisant, disponible sous `cloud_ceiling_ft` dans l'API (à convertir en mètres)
- **Activité thermique** — estimer les thermiques à partir de la température au sol (`temp_c`) et de la couverture nuageuse (`cloud`) pour savoir si les conditions seront dynamiques ou calmes
- **Visibilité** — vérifier que la visibilité (`vis_km`) est suffisante, notamment en cas de brume matinale en fond de vallée
- **Humidité** — une humidité élevée combinée à une température fraîche peut indiquer un risque de brouillard ou de nuages bas
- **Soleil** — vérifier que le jour soit toujours présent étant impossible de le dévoiler de nuit

### Fonctionnalités supplémentaires

- Ajouter un **résumé en tête de message** indiquant combien de sites sont volables sur le total (ex : `3 sites volables sur 10`)
- Permettre de configurer **plusieurs directions de vent acceptables** par site (certains sites fonctionnent aussi bien en nord qu'en nord-ouest)
- Envoyer un **deuxième message le soir** avec l'analyse à J+2 pour anticiper le week-end
- Ajouter une **alerte spéciale** si plusieurs sites sont volables simultanément sur une longue plage horaire

---
