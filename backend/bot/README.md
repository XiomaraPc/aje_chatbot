# AJEBOT Backend - Documentación


## Arquitectura del Sistema

### Stack Tecnológico

- **Backend**: Flask (Python 3.10.12)
- **LLM**: Claude Sonnet 4 (Anthropic)
- **Embeddings**: Amazon Titan (texto e imágenes)
- **Base de Datos Vectorial**: MongoDB Atlas
- **Cloud Services**: AWS Bedrock
- **Agentes**: LangChain

### Componentes Principales

```
backend/
├── bot/
│   └── serv/
│       ├── config/
│       │   └── logger_config.py      # Configuración de logging
│       ├── connections/
│       │   └── llm.py                # Cliente LLM (Claude)
│       ├── repositories/
│       │   ├── data_repository.py    # Repositorio de datos
│       │   └── vector_repository.py  # Repositorio vectorial
│       ├── services/
│       │   ├── agent_service.py      # Servicio del agente LangChain
│       │   ├── app_service.py        # Lógica de aplicación
│       │   ├── memory_service.py     # Gestión de memoria/historial
│       │   └── tools_service.py      # Herramientas del agente
│       ├── utils/
│       │   └── template_util.py      # Templates de prompts
│       ├── uploads/                  # Almacenamiento temporal de imagenes
│       ├── .env                      # Variables de entorno
│       ├── app.py                    # Aplicación Flask principal
│       └── requirements.txt          # Dependencias
```

## Funcionalidades

### 1. Procesamiento de Texto
- Consultas sobre estrategia de internacionalización
- Información detallada de productos AJE
- Análisis de mercados y expansión global
- Respuestas conversacionales contextuales

### 2. Reconocimiento Visual
- Identificación de productos mediante imágenes PNG
- Búsqueda vectorial multimodal
- Análisis de similitud visual
- Respuesta automática con información del producto

### 3. Gestión de Conversaciones
- Historial completo de chats por usuario
- Persistencia de mensajes
- Recuperación de conversaciones anteriores


## Configuración

### Variables de Entorno

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-xxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# AWS Bedrock
AWS_ACCESS_KEY_ID=AKIATSG6OR55ZNKWXTGD
AWS_SECRET_ACCESS_KEY=yZ9i/W/xxx
TABLE_NAME=aje-bot-data

# Modelos de Embedding
EMBEDDING_MODEL=amazon.titan-embed-text-v1
EMBEDDING_MODEL_IMAGE=amazon.titan-embed-image-v1

# MongoDB Atlas
MONGODB_URL=mongodb+srv://usuario:password@cluster0.zgce4wz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=CHATBOT_AJE
MONGODB_COLLECTION=Embeddings
MONGODB_COLLECTION_IMAGES=Products
```

### Dependencias

```txt
boto3==1.40.17
colorlog==6.9.0
flask==3.0.3
Flask-Cors==5.0.0
langchain==0.3.27
langchain-core==0.3.75
langchain-community==0.3.29
langchain-anthropic==0.3.13
langchain-aws==0.2.19
pymongo==4.6.0
python-dotenv==1.0.1
python-multipart==0.0.20
uvicorn==0.34.0
Unidecode==1.3.8
```

## Instalación y Ejecución

### Requisitos Previos
- Python 3.10.12
- Cuenta AWS con acceso a Bedrock
- API Key de Anthropic
- MongoDB Atlas configurado

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/XiomaraPc/aje_chatbot.git #Si no se ha clonado aún
cd backend/bot/serv
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
touch .env
# Editar .env con las credenciales
```

4. **Ejecutar el servidor**
```bash
flask --app app.py run
```

5. **Verificar funcionamiento**
```bash
curl http://localhost:5000/chats/user_123
```

El servidor estará disponible en `http://localhost:5000`

## Base de Datos

### MongoDB Collections

#### Embeddings (Texto)
```javascript
{
  "_id": ObjectId,
  "content": "texto del documento",
  "embedding": [1536 números flotantes],
  "metadata": {
    "source": "productos_aje",
    "tipo": "producto_individual"
  }
}
```

#### Products (Imágenes)
```javascript
{
  "_id": ObjectId,
  "image_embedding": [1024 números flotantes],
  "product_name": "Big Cola Cola",
  "product_id": "big_cola_350",
  "content_type": "image",
  "source": "aje_products"
}
```

### Índices Vectoriales

**Índice de Texto (vector_index):**
```json
{
  "fields": [{
    "type": "vector",
    "path": "embedding", 
    "numDimensions": 1536,
    "similarity": "cosine"
  }]
}
```

**Índice de Imágenes (vector_index_images):**
```json
{
  "fields": [{
    "type": "vector",
    "path": "embedding",
    "numDimensions": 1024, 
    "similarity": "cosine"
  }]
}
```

## Herramientas del Agente

### ConsultarEstrategia
- **Propósito**: Información sobre estrategia empresarial
- **Activación**: Keywords relacionados con internacionalización, mercados, expansión
- **Fuente**: Documentos vectorizados de estrategia AJE

### ConsultarProducto  
- **Propósito**: Información detallada de productos
- **Activación**: Nombres de productos, consultas sobre bebidas
- **Fuente**: Base de datos de productos AJE

### BuscarProductoImagen
- **Propósito**: Identificación visual de productos
- **Activación**: Mensaje "image" del endpoint upload-image
- **Proceso**: 
  1. Genera embedding de imagen con Titan
  2. Búsqueda vectorial en MongoDB
  3. Retorna nombre del producto
  4. Llama automáticamente a ConsultarProducto



## Manejo de Errores

### Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| 400 | Datos faltantes en request | Verificar payload JSON |
| 500 | Error interno del servidor | Revisar logs de aplicación |
| AccessDeniedException | Sin acceso a modelo Bedrock | Verificar permisos AWS |
| ConnectionError | Error de MongoDB | Verificar string de conexión |

### Logging

El sistema utiliza logging estructurado con diferentes niveles:

```python
# Configuración en logger_config.py
logging.INFO    # Información general
logging.WARNING # Advertencias
logging.ERROR   # Errores críticos
logging.DEBUG   # Información de desarrollo
```
