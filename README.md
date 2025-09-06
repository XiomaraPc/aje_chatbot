# AJEBOT - Guía de Instalación

## Descripción
Chatbot conversacional de AJE Group con backend Flask e interfaz React para consultas de texto e identificación visual de productos.

## Estructura
```
AJEBOT/
├── backend/bot/serv/    # API Flask + IA
└── fronted/             # Interfaz React
```

## Instalación Rápida

### 1. Clonar repositorio
```bash
git clone https://github.com/XiomaraPc/aje_chatbot.git
cd aje_chatbot
```

### 2. Backend
```bash
cd backend/bot/serv
pip install -r requirements.txt
# Configurar .env con credenciales
flask --app app.py run --port 5000
```

### 3. Frontend
```bash
cd fronted
npm install
npm start
```

## Acceso
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000

## Requisitos
- Python 3.10+
- Node.js 16+
- Credenciales AWS Bedrock, Anthropic, MongoDB Atlas

Ver documentación específica de cada módulo para detalles de configuración.