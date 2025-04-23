#!/bin/bash

# Script para instalar dependências e executar o aplicativo de análise de odds de futebol

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Iniciando o aplicativo..."
streamlit run src/app.py
