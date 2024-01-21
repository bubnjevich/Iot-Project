# Iot-Project

## Uputstvo za pokretanje
***
Pre pokretanja potrebno je dodati u `server` folder `.env` fajl  koji sadrzi sledeće:
```
token=
org=  
``` 
gde je posle znaka '=' za token i org potrebno navesti token i org koji se koriste.
Zatim unutar `infrastructure` direktorijuma dodati `.env` fajl koji sadrži sledeće:
```
INFLUXDB_DB=""
INFLUXDB_ADMIN_USER=""
INFLUXDB_ADMIN_PASSWORD=""
INFLUXDB_TOKEN=""

GRAFANA_USERNAME=""
GRAFANA_PASSWORD=""
```
gde je potrebno posle znaka = postaviti odgovarajuće vrednosti.
Potrebno je pokrenuti komandu `docker compose up` unutar `infrastructure` direktorijuma,
a zatim `server.py` skriptu  iz direktorijuma `server` i na kraju skriptu `main.py` koja pokreće aplikaciju.
Potrebni je, ukoliko nisu, instalirati odgovarajuće biblioteke za podršku rada (`Flask`,...)



FRONT APLIKACIJA: https://github.com/bubnjevich/IOT-Frontend