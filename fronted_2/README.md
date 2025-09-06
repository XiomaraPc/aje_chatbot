# AJEBOT Frontend

Interfaz web React para el chatbot conversacional de AJE Group con soporte para chat de texto e identificación visual de productos.

## Estructura del Proyecto

```
fronted/
├── package.json          # Configuración y dependencias
├── src/
│   ├── App.js           # Componente raíz
│   ├── index.js         # Punto de entrada
│   ├── index.css        # Estilos globales
│   └── components/
│       └── ChatBot.js   # Componente principal del chat
└── public/
    ├── index.html       # HTML base
    └── image.png        # Logo de AJE (agregar manualmente)
```

## Instalación

### Requisitos
- Node.js 16+
- npm

### Pasos

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm start
```

La aplicación se abrirá en `http://localhost:3000`

## Configuración

### Conexión con Backend

El frontend se conecta al backend en `http://localhost:5000`. Para cambiar la URL, editar en `src/components/ChatBot.js`:

```javascript
const API_BASE = 'http://localhost:PUERTO_DEL_BACKEND';
```


## Funcionalidades

- **Chat de texto**: Envío de mensajes al bot
- **Carga de imágenes**: Subida de archivos PNG para identificación de productos
- **Historial**: Navegación entre conversaciones anteriores
- **Interfaz responsive**: Diseño adaptable con colores corporativos de AJE
- **Formato de mensajes**: Renderizado de markdown (títulos, negritas, listas)

## Dependencias Principales

```json
{
  "react": "^19.1.1",
  "react-dom": "^19.1.1", 
  "lucide-react": "^0.263.1",
  "react-scripts": "5.0.1"
}
```

## Scripts Disponibles

```bash
npm start      # Servidor de desarrollo
npm run build  # Compilar para producción  
npm test       # Ejecutar tests
```

---

**Nota**: Asegúrese de que el backend esté corriendo antes de usar el frontend.