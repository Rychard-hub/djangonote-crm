# Redis diegimas su Docker (Windows)

## 1. Įdiekite Docker Desktop
- Atsisiųskite: https://www.docker.com/products/docker-desktop/
- Paleiskite ir įdiekite
- Paleiskite Docker Desktop programą

## 2. Paleiskite Redis konteinerį
```bash
# Pull Redis image
docker pull redis:latest

# Paleiskite Redis konteinerį
docker run -d -p 6379:6379 --name redis-server redis:latest

# Patikrinkite ar veikia
docker ps
# Turėtų matyti redis-server konteinerį
```

## 3. Testuokite Redis
```bash
# Prisijunkite prie Redis
docker exec -it redis-server redis-cli

# Testuokite
ping
# Atsakys: PONG

# Išeikite
exit
```

## 4. Patikrinkite Django konfigūraciją
```bash
cd c:/Users/ACER/Desktop/Django-CRM
python test_celery_setup.py
```

## 5. Paleiskite Celery su Redis
```bash
# Celery Worker
python -m celery -A crm_project worker -l info

# Celery Beat (kitame terminale)
python -m celery -A crm_project beat -l info
```

## 6. Stop Redis (kai reikia)
```bash
docker stop redis-server
docker rm redis-server
```

## Privalumai:
✅ Veikia iš karto be WSL
✅ Lengvai valdomas
✅ Automatiškai startuoja
✅ Tinka developmentui
