#!/bin/bash

# Script per avviare lo stack completo Casa&Più in locale con Docker Compose

set -e

echo "🏠 Casa&Più - Avvio Stack Locale"
echo "=================================="

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Controlla se Docker è in esecuzione
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker non è in esecuzione. Avvia Docker Desktop e riprova.${NC}"
    exit 1
fi

# Controlla se esiste .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  File .env non trovato. Copiando da .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Modifica il file .env con le tue credenziali prima di continuare.${NC}"
    read -p "Premi INVIO quando hai configurato .env..."
fi

# Controlla se esiste firebase-key.json
if [ ! -f backend/firebase-key.json ]; then
    echo -e "${YELLOW}⚠️  File backend/firebase-key.json non trovato.${NC}"
    echo -e "${YELLOW}   Le notifiche push non funzioneranno senza questo file.${NC}"
    echo -e "${YELLOW}   Scaricalo da Firebase Console > Impostazioni Progetto > Service Accounts${NC}"
    read -p "Premi INVIO per continuare comunque..."
fi

# Ferma eventuali container esistenti
echo -e "\n${YELLOW}🛑 Fermando container esistenti...${NC}"
docker-compose down

# Build delle immagini
echo -e "\n${GREEN}🔨 Building immagini Docker...${NC}"
docker-compose build

# Avvia i servizi
echo -e "\n${GREEN}🚀 Avvio servizi...${NC}"
docker-compose up -d postgres redis

# Attendi che postgres sia pronto
echo -e "\n${YELLOW}⏳ Attendo che PostgreSQL sia pronto...${NC}"
sleep 5

# Avvia il backend
echo -e "\n${GREEN}🚀 Avvio backend...${NC}"
docker-compose up -d backend

# Mostra lo stato dei servizi
echo -e "\n${GREEN}✅ Stack avviato con successo!${NC}"
echo -e "\n📊 Stato servizi:"
docker-compose ps

echo -e "\n${GREEN}🌐 Servizi disponibili:${NC}"
echo -e "  Backend API:       ${GREEN}http://localhost:8080${NC}"
echo -e "  API Docs:          ${GREEN}http://localhost:8080/docs${NC}"
echo -e "  PostgreSQL:        ${GREEN}localhost:5432${NC}"
echo -e "  Redis:             ${GREEN}localhost:6379${NC}"

echo -e "\n${YELLOW}💡 Comandi utili:${NC}"
echo -e "  Visualizza logs:   ${GREEN}docker-compose logs -f${NC}"
echo -e "  Ferma stack:       ${GREEN}docker-compose down${NC}"
echo -e "  Riavvia:           ${GREEN}docker-compose restart${NC}"
echo -e "  Avvia PgAdmin:     ${GREEN}docker-compose --profile tools up -d pgadmin${NC}"
echo -e "                     ${GREEN}http://localhost:5050${NC}"

echo -e "\n${GREEN}🎉 Setup completato! Ora avvia il frontend:${NC}"
echo -e "  ${GREEN}cd frontend && npm install && npm start${NC}"
