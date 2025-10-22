#!/bin/bash

# Script per fermare lo stack Casa&Più

set -e

echo "🛑 Fermando Casa&Più Stack..."

# Ferma tutti i container
docker-compose down

echo "✅ Stack fermato con successo!"

# Opzione per rimuovere anche i volumi
read -p "Vuoi rimuovere anche i dati del database? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker-compose down -v
    echo "🗑️  Volumi rimossi"
fi
