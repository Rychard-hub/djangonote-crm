# Skybridge CRM - Freelancer Management System 

Modernus CRM sistema su Django REST API ir React frontend, integruota su Skybridge/MCP serveriu.

## 🏗️ Architektūra

```
[ React Frontend (localhost:3000) ]
        ↓
[ Django REST API (localhost:8000) ]
        ↓
[ Django Business Logic ]
        ↓
[ SQLite Database ]
```

## 🚀 Grelis paleidimas

### 1. Django Backend
```bash
cd c:\Users\ACER\Desktop\Django-CRM
python manage.py runserver
```
Backend veiks adresu: http://127.0.0.1:8000

### 2. React Frontend  
```bash
cd skybridge_crm
npm run dev
```
Frontend veiks adresu: http://localhost:3000

### 3. MCP Server (papildomai)
```bash
cd c:\Users\ACER\Desktop\Django-CRM
python mcp_server_final.py
```

## 🔐 Autentifikacija

Testinis vartotojas:
- El. paštas: `test@example.com`
- Slaptažodis: `test123`

## 📊 Funkcionalumai

### ✅ Veikiantys funkcionalumai:
- **Lead'ų valdymas** - CRUD operacijos
- **Dashboard statistika** - Realus laiko duomenys
- **JWT autentifikacija** - Saugus prisijungimas
- **Statusų valdymas** - Naujas → Susisiektas → Pasiūlymas → Laimėtas/Pralaimėtas
- **Komentarų sistema** - Bendravimo istorija
- **Užduočių valdymas** - Follow-up'ai ir užduotys
- **MCP integracija** - 9 CRM valdymo įrankiai

### 🔧 API Endpoint'ai:
```
GET  /api/leads/                    - Lead'ų sąrašas
POST /api/leads/                    - Sukurti lead'ą
GET  /api/leads/{id}/               - Lead'o detalės
PATCH /api/leads/{id}/update_status/ - Atnaujinti statusą
POST /api/leads/{id}/add_comment/   - Pridėti komentarą
POST /api/leads/{id}/add_task/      - Pridėti užduotį
GET  /api/leads/dashboard_stats/    - Dashboard statistika
GET  /api/auth/token/                - JWT autentifikacija
```

### 🤖 MCP Įrankiai:
- `list_leads` - Lead'ų sąrašas su filtravimu
- `get_lead_details` - Lead'o detalės  
- `create_lead` - Naujo lead'o kūrimas
- `update_lead_status` - Statuso keitimas
- `get_dashboard_summary` - Dashboard statistika
- `get_followups` - Follow-up'ai (artėjantys/vėluojantys)
- `add_comment` - Komentarų pridėjimas
- `add_task` - Užduočių pridėjimas
- `get_activities` - Veiksmų istorija

## 🛠️ Technologijos

### Backend:
- **Django 6.0.6** - Web framework
- **Django REST Framework** - API
- **JWT Authentication** - Autentifikacija
- **SQLite** - Duomenų bazė
- **CORS Headers** - Cross-origin

### Frontend:
- **React 18** - UI framework  
- **TypeScript** - Tipų sauga
- **Vite** - Build tool
- **Tailwind CSS** - Stilingas

### MCP Integration:
- **Model Context Protocol** - AI agentų integracija
- **9 CRM įrankiai** - Pilnas valdymas
- **JWT autentifikacija** - Saugumas

## 📱 Vartotojo sąsaja

### Dashboard:
- Lead'ų statistika
- Biudžeto apžvalga
- Artėjantys ir vėluojantys follow-up'ai
- Statusų pasiskirstymas

### Lead valdymas:
- Lead'ų sąrašas su filtravimu
- Detali lead'o informacija
- Statusų keitimas
- Komentarų ir užduočių pridėjimas

### MCP Skybridge:
- AI agentų integracija
- Automatizuotas lead'ų valdymas
- Realus laiko duomenų mainai

## 🔧 Testavimas

### API testavimas:
```bash
cd c:\Users\ACER\Desktop\Django-CRM
python test_api.py
```

### MCP testavimas:
```bash
cd c:\Users\ACER\Desktop\Django-CRM
python mcp_server_final.py
```

### Frontend testavimas:
Atidarykite http://localhost:3000 naršyklėje

## 📈 Būsimo plėtra

### Planuojami funkcionalumai:
- [ ] Realus laiko notifikacijos
- [ ] Paštų integracija
- [ ] Dokumentų valdymas
- [ ] Raportų generavimas
- [ ] Mobilioji aplikacija
- [ ] Daugiau MCP įrankių

## 🐧 Trikčių sprendimas

### TypeScript klaidos:
- Daugelis TypeScript klaidų yra susijusios su MCP serverio mock'ais
- Frontendas veikia nepaisant klaidų
- Galima ignoruoti development režime

### CORS problemos:
- Django backend turi būti paleistas
- CORS nustatymai konfigūruoti settings.py

### Autentifikacija:
- JWT tokenai galioja 60 min
- Refresh tokenai galioja 7 dienas

## 📞 Kontaktai

CRM sistema paruošta naudojimui su Django backend ir React frontend!
