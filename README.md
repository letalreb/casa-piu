# Casa&Più 🏠 - Family Expense Management App

**Casa&Più** è un'applicazione completa per la gestione delle spese familiari legate a immobili e veicoli, con promemoria intelligenti, calcolo IMU automatico, generazione F24, gestione bollette, suggerimenti AI e notifiche push.

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Tech Stack](#️-tech-stack)
- [Architettura](#-architettura)
- [Requisiti](#-requisiti)
- [Installazione Locale](#-installazione-locale)
- [Configurazione](#️-configurazione)
- [Deployment](#-deployment)
- [API Endpoints](#-api-endpoints)
- [Struttura Progetto](#-struttura-progetto)
- [Contribuire](#-contribuire)

## ✨ Caratteristiche

### 🏡 Gestione Immobili
- CRUD completo per immobili (indirizzo, comune, categoria catastale, rendita)
- **Calcolo IMU automatico** basato su rendita catastale e categoria
- **Generazione PDF F24** per pagamento IMU
- Promemoria automatici 15 giorni prima delle scadenze (16/06 e 16/12)

### 🚗 Gestione Veicoli
- CRUD completo per veicoli (targa, marca, modello, anno)
- Promemoria automatici per:
  - Bollo auto
  - Assicurazione
  - Revisione

### 💰 Gestione Spese
- Inserimento manuale di spese (bollette, condominio, rate, manutenzioni)
- Upload PDF bollette con **OCR automatico** per estrazione dati
- Tracciamento stato pagamenti (pending, paid, overdue)
- Dashboard con riepilogo mensile

### 🤖 Automazioni Intelligenti
- Toggle per attivare automazioni per ogni bene:
  - Calcolo IMU automatico
  - Generazione F24
  - OCR su bollette
  - Suggerimenti AI per risparmio

### 🧠 AI Suggestions
- Analisi automatica delle spese
- Suggerimenti personalizzati per risparmiare
- Integrazione con Claude (Anthropic) o OpenAI GPT

### 🔔 Sistema Notifiche
- **Push notifications** via Firebase Cloud Messaging
- Scheduler automatico per promemoria (APScheduler)
- Endpoint manuale per test notifiche

### 🔐 Autenticazione
- **Google OAuth2** via Supabase Auth
- Gestione profilo utente
- Token JWT per API backend

## 🛠️ Tech Stack

### Frontend
- **Ionic 7** + **React** + **TypeScript**
- **Capacitor** per build mobile (iOS/Android)
- **React Router** per navigazione
- **Axios** per chiamate API
- **Supabase JS SDK** per autenticazione
- **Firebase SDK** per push notifications

### Backend
- **FastAPI** (Python 3.12)
- **Uvicorn** ASGI server
- **SQLAlchemy** ORM
- **PostgreSQL** database (Supabase)
- **APScheduler** per task automatici
- **ReportLab** per generazione PDF F24
- **Pytesseract** per OCR
- **Anthropic/OpenAI** per AI suggestions

### Cloud & Hosting
- **Backend**: Render.com (Docker)
- **Database**: Supabase (PostgreSQL + Auth)
- **Frontend**: Firebase Hosting
- **Push Notifications**: Firebase Cloud Messaging

## 📐 Architettura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Ionic     │◄────►│    FastAPI   │◄────►│  Supabase   │
│   React     │      │    Backend   │      │  PostgreSQL │
│   Frontend  │      └──────────────┘      └─────────────┘
└─────────────┘             │
      │                     │
      │                     ▼
      │              ┌──────────────┐
      │              │  APScheduler │
      │              │   (Cron)     │
      │              └──────────────┘
      │                     │
      ▼                     ▼
┌─────────────┐      ┌──────────────┐
│  Firebase   │      │   Firebase   │
│   Hosting   │      │     FCM      │
└─────────────┘      └──────────────┘
```

## 📦 Requisiti

- **Node.js** 18+ e npm
- **Python** 3.12+
- **Docker** (opzionale, per deployment)
- **PostgreSQL** 14+ (o account Supabase)
- **Account Firebase** (per hosting e notifiche)
- **Account Render.com** (per backend hosting)

## 🚀 Installazione Locale

### 1. Clone del Repository

```bash
git clone https://github.com/yourusername/casa-piu.git
cd casa-piu
```

### 2. Setup Backend

```bash
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Copia file .env
cp .env.example .env
# Modifica .env con le tue credenziali
```

### 3. Setup Frontend

```bash
cd frontend

# Installa dipendenze
npm install

# Crea file .env
cp .env.example .env
# Modifica .env con le tue credenziali
```

### 4. Database Setup

#### Opzione A: Supabase (Raccomandato)

1. Vai su [Supabase](https://app.supabase.com)
2. Crea un nuovo progetto
3. Esegui il file `supabase/schema.sql` nell'editor SQL
4. Copia la connection string in `.env`

#### Opzione B: PostgreSQL Locale

```bash
# Crea database
createdb casapiu

# Esegui migrations
cd backend
alembic upgrade head
```

### 5. Avvio Applicazione

#### Backend

```bash
cd backend
uvicorn main:app --reload --port 8080
```

API disponibile su `http://localhost:8080`
Documentazione: `http://localhost:8080/docs`

#### Frontend

```bash
cd frontend
npm start
# oppure per iOS/Android
ionic capacitor run ios
ionic capacitor run android
```

App disponibile su `http://localhost:8100`

## ⚙️ Configurazione

### Backend `.env`

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/casapiu
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
FIREBASE_KEY_PATH=/path/to/firebase-key.json
OPENAI_API_KEY=sk-...  # Opzionale
ANTHROPIC_API_KEY=sk-ant-...  # Opzionale
REDIS_URL=redis://localhost:6379/0  # Opzionale
```

### Frontend `.env`

```env
VITE_API_URL=http://localhost:8080/api
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-app.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
VITE_FIREBASE_VAPID_KEY=your_vapid_key
```

### Supabase Auth - Google OAuth

1. Vai su **Authentication** > **Providers** nel dashboard Supabase
2. Abilita **Google**
3. Aggiungi Google OAuth credentials da [Google Cloud Console](https://console.cloud.google.com)
4. Aggiungi redirect URL: `https://your-project.supabase.co/auth/v1/callback`

### Firebase Cloud Messaging

1. Vai su [Firebase Console](https://console.firebase.google.com)
2. Crea progetto (o usa esistente)
3. Abilita **Cloud Messaging**
4. Genera **Service Account Key** (Impostazioni Progetto > Service Accounts)
5. Scarica `firebase-key.json` e salvalo in `backend/`
6. Genera **Web Push Certificate** (Cloud Messaging > Web Configuration)
7. Copia VAPID key in frontend `.env`

## 🚢 Deployment

### Backend (Render.com)

1. Crea account su [Render.com](https://render.com)
2. Connetti repository GitHub
3. Crea nuovo **Web Service**
4. Imposta:
   - **Environment**: Docker
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Port**: 8080
5. Aggiungi variabili d'ambiente dal dashboard Render
6. Deploy automatico al push su `main`

### Frontend (Firebase Hosting)

```bash
cd frontend

# Build produzione
npm run build

# Login Firebase
firebase login

# Inizializza progetto
firebase init hosting

# Deploy
firebase deploy --only hosting
```

### Script Automatico

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Registra nuovo utente
- `POST /api/auth/verify-token` - Verifica token Supabase
- `GET /api/auth/profile` - Ottieni profilo utente
- `PUT /api/auth/profile` - Aggiorna profilo

### Assets (Immobili/Veicoli)
- `GET /api/assets/` - Lista beni (con filtri)
- `GET /api/assets/{id}` - Dettagli bene
- `POST /api/assets/` - Crea bene
- `PUT /api/assets/{id}` - Aggiorna bene
- `DELETE /api/assets/{id}` - Elimina bene

### Expenses (Spese)
- `GET /api/expenses/` - Lista spese
- `GET /api/expenses/{id}` - Dettagli spesa
- `POST /api/expenses/` - Crea spesa
- `PUT /api/expenses/{id}` - Aggiorna spesa
- `DELETE /api/expenses/{id}` - Elimina spesa

### Reminders
- `GET /api/reminders/` - Lista promemoria
- `POST /api/reminders/` - Crea promemoria
- `POST /api/reminders/run` - Esegui check manuale

### Automations
- `GET /api/automations/{asset_id}` - Ottieni automazioni bene
- `POST /api/automations/` - Crea automazioni
- `PUT /api/automations/{id}` - Aggiorna automazioni

### IMU & F24
- `POST /api/f24/calculate-imu` - Calcola IMU
  ```json
  {
    "rendita": 1000.00,
    "categoria": "A/2",
    "comune": "Roma"
  }
  ```
- `POST /api/f24/generate` - Genera PDF F24
  ```json
  {
    "asset_id": 1,
    "payment_type": "primo"
  }
  ```

### AI Suggestions
- `POST /api/suggestions/ai` - Ottieni suggerimenti AI
  ```json
  {
    "asset_id": 1,
    "period_months": 6
  }
  ```

## 📁 Struttura Progetto

```
casa-piu/
├── backend/
│   ├── api/                    # API routes
│   │   ├── auth.py
│   │   ├── assets.py
│   │   ├── expenses.py
│   │   ├── reminders.py
│   │   ├── automations.py
│   │   ├── suggestions.py
│   │   └── f24.py
│   ├── models/                 # Database models
│   │   └── __init__.py
│   ├── schemas/                # Pydantic schemas
│   │   └── __init__.py
│   ├── utils/                  # Utilities
│   │   ├── auth.py             # Authentication
│   │   ├── imu_calc.py         # IMU calculator
│   │   ├── f24_pdf.py          # F24 PDF generator
│   │   ├── ocr_parser.py       # OCR parser
│   │   ├── notifier.py         # Firebase notifications
│   │   └── scheduler.py        # APScheduler
│   ├── static/                 # Static files (F24 PDFs)
│   ├── main.py                 # FastAPI app
│   ├── database.py             # DB config
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Assets.tsx
│   │   │   ├── Expenses.tsx
│   │   │   ├── Reminders.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/         # Reusable components
│   │   ├── services/           # API services
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── notifications.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── capacitor.config.ts
│   ├── firebase.json
│   ├── package.json
│   └── .env.example
│
├── deploy/
│   ├── deploy.sh               # Deployment script
│   └── render.yaml             # Render config
│
├── supabase/
│   └── schema.sql              # Database schema
│
└── README.md
```

## 🧪 Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## 📊 Database Schema

```sql
users (
  id, email, name, supabase_id, created_at, updated_at
)

assets (
  id, user_id, type, name, details_json, created_at, updated_at
)

expenses (
  id, user_id, asset_id, category, amount, due_date, status, description
)

reminders (
  id, asset_id, type, date, message, notified, created_at
)

automations (
  id, asset_id, imu_calc, f24_gen, ocr, ai_suggestions
)

documents (
  id, asset_id, file_url, file_type, parsed_data_json, created_at
)
```

## 🐛 Troubleshooting

### Backend non si avvia

```bash
# Verifica dependencies
pip install -r requirements.txt

# Verifica database connection
psql $DATABASE_URL

# Check logs
uvicorn main:app --reload --log-level debug
```

### Frontend non si connette al backend

- Verifica `VITE_API_URL` in `.env`
- Controlla CORS settings in `main.py`
- Verifica che il backend sia in esecuzione

### Notifiche push non funzionano

- Verifica Firebase configuration
- Controlla che `firebase-key.json` esista
- Verifica VAPID key nel frontend
- Testa con endpoint `/reminders/run`

## 🤝 Contribuire

1. Fork del repository
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 👨‍💻 Autori

Sviluppato con ❤️ da [Your Name]

## 🙏 Ringraziamenti

- [Ionic Framework](https://ionicframework.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)
- [Firebase](https://firebase.google.com/)
- [Render](https://render.com/)

---

**Casa&Più** - Gestisci le tue proprietà con intelligenza! 🏠✨