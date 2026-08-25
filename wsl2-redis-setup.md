# Redis diegimas su WSL2 (Windows)

## 1. Įdiekite WSL2 (jei dar neturite)
```bash
# PowerShell Administrator režime
wsl --install

# Restart kompiuterį
# Paleiskite Ubuntu iš Start meniu
```

## 2. Įdiekite Redis Ubuntuje
```bash
# Atnaujinkite paketus
sudo apt update && sudo apt upgrade -y

# Įdiekite Redis
sudo apt install redis-server -y

# Paleiskite Redis servisą
sudo service redis-server start

# Įjunkite auto-start
sudo systemctl enable redis-server
```

## 3. Konfigūruokite Redis
```bash
# Atidarykite konfigūraciją
sudo nano /etc/redis/redis.conf

# Pakeiskite:
bind 0.0.0.0  # Leidžia išorinius prisijungimus
# Išsaugokite (Ctrl+X, Y, Enter)

# Restart Redis
sudo service redis-server restart
```

## 4. Testuokite Redis
```bash
# Testuokite connection
redis-cli ping
# Atsakys: PONG

# Testuokite iš Windows
redis-cli -h localhost -p 6379 ping
```

## 5. Django konfigūracija patikrinimas
```bash
cd /mnt/c/Users/ACER/Desktop/Django-CRM
python test_celery_setup.py
```

## 6. Paleiskite Celery
```bash
# Celery Worker
python -m celery -A crm_project worker -l info

# Celery Beat (kitame terminale)
python -m celery -A crm_project beat -l info
```

## Privalumai:
✅ Tikras Redis (ne Docker)
✅ Geresnis performance
✅ Pilna Redis funkcionalumas
✅ Tinka productionui
