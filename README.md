# ⚡ WAMO - WhatsApp Message App for Odoo

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Odoo](https://img.shields.io/badge/Odoo-14.0+-purple.svg)](https://www.odoo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org)
[![Node.js](https://img.shields.io/badge/Node.js-18.0+-green.svg?logo=node.js&logoColor=white)](https://nodejs.org)
[![SCSS](https://img.shields.io/badge/SCSS-CC6699?logo=sass&logoColor=white)](https://sass-lang.com)


WAMO es un módulo de integración que permite conectar WhatsApp Web con el sistema ERP Odoo 16, proporcionando a las empresas una solución completa de comunicación empresarial. Permite gestionar contactos, mensajes, chats, productos y plantillas desde la interfaz de Odoo, usando la librería whatsapp-web.js.

---

## 📋 Tabla de Contenidos

- [⚡ WAMO - WhatsApp Message App for Odoo](#-wamo---whatsapp-message-app-for-odoo)
  - [📋 Tabla de Contenidos](#-tabla-de-contenidos)
  - [📌 Características principales](#-características-principales)
  - [📁 Estructura del proyecto](#-estructura-del-proyecto)
    - [📂 Descripción detallada de módulos](#-descripción-detallada-de-módulos)
  - [🛠️ Requisitos previos](#️-requisitos-previos)
  - [📦 Instalación](#-instalación)
    - [1. Clonar o descargar el proyecto](#1-clonar-o-descargar-el-proyecto)
    - [2. Instalar dependencias](#2-instalar-dependencias)
      - [Backend (Odoo)](#backend-odoo)
      - [WhatsApp Web Service](#whatsapp-web-service)
    - [3. Configurar estructura de carpetas](#3-configurar-estructura-de-carpetas)
  - [⚙️ Configuración](#️-configuración)
    - [Variables de entorno del microservicio WhatsApp](#variables-de-entorno-del-microservicio-whatsapp)
    - [🗄️ Preparación de la base de datos](#️-preparación-de-la-base-de-datos)
  - [🚀 Uso](#-uso)
    - [Ejecución del microservicio WhatsApp](#ejecución-del-microservicio-whatsapp)
    - [Activación desde Odoo](#activación-desde-odoo)
    - [Ejecución con logs](#ejecución-con-logs)
  - [🔧 Personalización](#-personalización)
  - [🧪 Validación y formato de datos](#-validación-y-formato-de-datos)
  - [🐞 Solución de problemas](#-solución-de-problemas)
    - [❌ No se genera el código QR](#-no-se-genera-el-código-qr)
    - [❌ No se sincronizan contactos](#-no-se-sincronizan-contactos)
    - [❌ Error al enviar mensajes](#-error-al-enviar-mensajes)
  - [📄 Registro de logs](#-registro-de-logs)
  - [⚠️ Limitaciones](#️-limitaciones)
  - [🤝 Contribución](#-contribución)
  - [📄 Licencia](#-licencia)

---

## 📌 Características principales

- ✅ Escaneo de códigos QR para autenticación y vinculación de cuentas WhatsApp Web
- 🔄 Sincronización de contactos y visualización de hilos de conversación
- ⚙️ Envío y recepción de mensajes, archivos, imágenes y productos desde Odoo
- 📊 Soporte para mensajes predefinidos y automatización básica
- 🧩 Integración completa con módulos estándar de Odoo: ventas, productos, website

---

## 📁 Estructura del proyecto

```
wamo:.
├───.vscode                      # Configuración del editor Visual Studio Code
├───config                       # Archivos de configuración del módulo
│   └───__pycache__              # Cache de Python
├───controllers                  # Controladores de endpoints HTTP
│   └───__pycache__
├───data                         # Datos iniciales y configuraciones XML
├───logs                         # Logs del sistema y servicios
│   └───controllers              # Logs específicos de controladores
│       └───2025
├───models                       # Modelos ORM de Odoo
│   ├───mixins                   # Clases mixins reutilizables
│   │   └───__pycache__
│   └───__pycache__
├───security                     # Reglas de acceso y permisos
├───services                     # Servicios de negocio y lógica empresarial
│   ├───controller               # Servicios para controladores
│   │   └───__pycache__
│   ├───model                    # Servicios para modelos
│   │   └───__pycache__
│   └───__pycache__
├───static                       # Recursos estáticos (JS, CSS, imágenes)
│   ├───description              # Descripción del módulo para Odoo Apps
│   └───src                      # Código fuente frontend
│       ├───assets               # Recursos multimedia y scripts
│       │   ├───img              # Imágenes, stickers y wallpapers
│       │   │   ├───stickers
│       │   │   └───wallpaper
│       │   ├───js               # Scripts JavaScript organizados por funcionalidad
│       │   │   ├───aplication   # Lógica principal de la aplicación
│       │   │   │   ├───chat_handler      # Manejo de chats
│       │   │   │   ├───emojis            # Gestión de emojis
│       │   │   │   └───stickers          # Gestión de stickers
│       │   │   ├───basic                 # Funciones básicas
│       │   │   ├───connection            # Gestión de conexiones
│       │   │   │   ├───managers          # Administradores de conexión
│       │   │   │   ├───services          # Servicios de conexión
│       │   │   │   ├───ui                # Interfaz de usuario para conexión
│       │   │   │   └───utils             # Utilidades de conexión
│       │   │   ├───general               # Scripts generales
│       │   │   │   ├───navigation        # Navegación
│       │   │   │   ├───Responsive        # Diseño responsivo
│       │   │   │   └───template          # Plantillas
│       │   │   │       └───modules       # Módulos de plantillas
│       │   │   └───messages              # Gestión de mensajes
│       │   │       ├───manager           # Administrador de mensajes
│       │   │       ├───render            # Renderizado de mensajes
│       │   │       ├───service           # Servicios de mensajes
│       │   │       └───utils             # Utilidades de mensajes
│       │   └───media                     # Archivos multimedia
│       │       ├───audio                 # Archivos de audio
│       │       └───files                 # Archivos diversos
│       └───styles                        # Estilos CSS/SCSS
│           ├───basic                     # Estilos básicos
│           └───scss                      # Archivos SCSS
├───utils                                 # Utilidades generales del sistema
│   ├───log                               # Sistema de logging
│   │   ├───logs                          # Archivos de log
│   │   │   └───extra                     # Logs adicionales
│   │   └───__pycache__
│   ├───logs                              # Logs organizados por fecha
│   │   └───2025
│   ├───response                          # Utilidades para respuestas HTTP
│   │   └───__pycache__
│   ├───validation                        # Validaciones de datos
│   │   └───__pycache__
│   └───__pycache__
├───views                                 # Vistas XML de Odoo
│   ├───aplication                        # Vistas de la aplicación principal
│   │   ├───base                          # Vistas base
│   │   │   ├───components                # Componentes base
│   │   │   └───scripts                   # Scripts de vistas base
│   │   ├───chats                         # Vistas de chats
│   │   │   └───components
│   │   ├───contacts                      # Vistas de contactos
│   │   │   └───components
│   │   ├───default_message               # Vistas de mensajes predeterminados
│   │   │   └───components
│   │   ├───messages                      # Vistas de mensajes
│   │   │   └───components
│   │   └───products                      # Vistas de productos
│   │       └───components
│   ├───configuration                     # Vistas de configuración
│   ├───connection                        # Vistas de conexión
│   │   └───components
│   ├───error                             # Vistas de error
│   └───landing                           # Vistas de página principal
│       └───components
└───__pycache__                          # Cache de Python del directorio raíz
```

### 📂 Descripción detallada de módulos

| 📁 Carpeta / Subcarpeta       | Descripción                                                                                          |
|-------------------------------|------------------------------------------------------------------------------------------------------|
| `.vscode/`                    | Configuración del editor Visual Studio Code.                                                         |
| `config/`                     | Archivos de configuración del módulo.                                                               |
| `controllers/`               | Controladores de endpoints HTTP para la comunicación backend.                                        |
| `data/`                      | Contiene datos iniciales, configuraciones y archivos XML.                                            |
| `logs/`                      | Archivos de log del sistema y eventos registrados.                                                   |
| `logs/controllers/`         | Logs específicos generados por los controladores, organizados por año.                              |
| `models/`                    | Modelos ORM de Odoo que representan entidades de negocio.                                            |
| `models/mixins/`            | Clases `mixin` reutilizables para extender funcionalidad en modelos.                                 |
| `security/`                  | Definiciones de seguridad, reglas de acceso y permisos.                                              |
| `services/`                  | Servicios que encapsulan la lógica de negocio y funciones reutilizables.                            |
| `services/controller/`      | Servicios relacionados con los controladores.                                                        |
| `services/model/`           | Servicios asociados al comportamiento de los modelos.                                                |
| `static/`                    | Recursos estáticos del módulo.                                                                      |
| `static/description/`       | Descripción del módulo para Odoo Apps.                                                              |
| `static/src/`               | Código fuente frontend del módulo.                                                                  |
| `static/src/assets/`        | Archivos multimedia (imágenes, stickers, fondos, scripts).                                           |
| `static/src/assets/js/`     | Scripts JavaScript divididos por funcionalidad.                                                      |
| `static/src/assets/js/aplication/`     | Lógica principal del frontend de la aplicación.                                        |
| `static/src/assets/js/aplication/chat_handler/` | Manejo de chats en frontend.                                         |
| `static/src/assets/js/aplication/emojis/`       | Gestión de emojis.                                                  |
| `static/src/assets/js/aplication/stickers/`     | Gestión de stickers.                                                |
| `static/src/assets/js/basic/`         | Funciones JS básicas del sistema.                                      |
| `static/src/assets/js/connection/`    | Gestión de conexiones cliente-servidor.                               |
| `static/src/assets/js/connection/managers/` | Administración de conexiones.                                     |
| `static/src/assets/js/connection/services/` | Servicios de conexión.                                            |
| `static/src/assets/js/connection/ui/`       | Interfaz de usuario para conexión.                                |
| `static/src/assets/js/connection/utils/`    | Utilidades de conexión.                                           |
| `static/src/assets/js/general/`      | Scripts generales reutilizables.                                     |
| `static/src/assets/js/general/navigation/` | Lógica de navegación.                                              |
| `static/src/assets/js/general/Responsive/` | Soporte para diseño responsivo.                                     |
| `static/src/assets/js/general/template/modules/` | Plantillas de módulos.                                         |
| `static/src/assets/js/messages/`     | Módulo de gestión de mensajes.                                      |
| `static/src/assets/js/messages/manager/`     | Administrador de mensajes.                                    |
| `static/src/assets/js/messages/render/`      | Lógica de renderizado de mensajes.                            |
| `static/src/assets/js/messages/service/`     | Servicios de mensajes.                                        |
| `static/src/assets/js/messages/utils/`       | Utilidades de mensajes.                                       |
| `static/src/assets/media/`          | Archivos multimedia adicionales (audio, documentos, etc.).         |
| `static/src/styles/`               | Archivos de estilos CSS y SCSS.                                    |
| `static/src/styles/basic/`         | Estilos base generales.                                           |
| `static/src/styles/scss/`          | Archivos SCSS para diseño modular y mantenible.                    |
| `utils/`                           | Utilidades generales del sistema.                                  |
| `utils/log/`                       | Sistema de logging propio del módulo.                              |
| `utils/log/logs/extra/`            | Logs adicionales especializados.                                   |
| `utils/logs/2025/`                 | Logs organizados por año.                                          |
| `utils/response/`                 | Funciones de ayuda para respuestas HTTP estándar.                  |
| `utils/validation/`               | Validaciones de datos, tipos y estructuras.                        |
| `views/`                          | Vistas XML del módulo para la interfaz de Odoo.                    |
| `views/aplication/`              | Vistas de la aplicación principal.                                 |
| `views/aplication/base/`         | Componentes y scripts base de vistas.                              |
| `views/aplication/chats/`        | Vistas específicas para manejo de chats.                           |
| `views/aplication/contacts/`     | Vistas de contactos.                                               |
| `views/aplication/default_message/` | Vistas de mensajes predeterminados.                              |
| `views/aplication/messages/`     | Vistas para mensajes generales.                                    |
| `views/aplication/products/`     | Vistas de productos y catálogo.                                    |
| `views/configuration/`           | Vistas para configuración del sistema.                             |
| `views/connection/`              | Vistas asociadas a la conexión de cuentas.                         |
| `views/error/`                   | Vistas para manejo de errores.                                     |
| `views/landing/`                 | Vistas de la página principal (landing page).                      |
| `__pycache__/`                   | Cache de compilación de Python (no modificar manualmente).         |

> ℹ️ **Nota:** Las carpetas `__pycache__/` son generadas automáticamente por Python y no deben ser modificadas manualmente.

---

## 🛠️ Requisitos previos

- Odoo 16 (con módulos base, ventas, productos y website)
- Node.js >= 18.0 (para usar whatsapp-web.js)
- Python >= 3.8
- Librerías JavaScript: whatsapp-web.js, qrcode.min.js, sweetalert2.min.js

---

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/tuusuario/wamo.git
cd wamo
```

### 2. Instalar dependencias

#### Backend (Odoo)
Asegúrate de tener Odoo 16 configurado y corriendo con los módulos requeridos.

#### WhatsApp Web Service
```bash
npm install whatsapp-web.js qrcode-terminal
```

### 3. Configurar estructura de carpetas

```bash
mkdir -p logs screenshots
```

---

## ⚙️ Configuración

### Variables de entorno del microservicio WhatsApp

Crea un archivo `.env` con las siguientes variables:

```env
PORT=3000
SESSION_NAME=wamo-session
```

### 🗄️ Preparación de la base de datos

Odoo se encargará de crear las tablas necesarias al instalar el módulo. Asegúrate de activar los módulos: `base`, `sales_team`, `product`, `website`.

---

## 🚀 Uso

### Ejecución del microservicio WhatsApp

```bash
node index.js
```

### Activación desde Odoo

1. Ir al módulo WAMO
2. Escanear el código QR desde el panel de autenticación
3. Usar la interfaz para gestionar contactos, mensajes y productos

### Ejecución con logs

```bash
node index.js > ./logs/wamo_2025-06-21.log
```

---

## 🔧 Personalización

| Componente | Función |
|------------|---------|
| `models/` | Definir nuevas funcionalidades o entidades |
| `views/components/*.xml` | Personalizar la UI o el layout del frontend |
| `data/ir_config_parameter_data.xml` | Cambiar parámetros del sistema por defecto |
| `controllers/` | Añadir nuevos endpoints o controladores |

---

## 🧪 Validación y formato de datos

- **Formatos de entrada**: JSON desde WhatsApp Web y ORM Odoo
- **Validación de sesiones**: Contactos y mensajes vía `authMiddleware.js`
- **Verificación de integridad**: Al compartir productos desde Odoo

---

## 🐞 Solución de problemas

### ❌ No se genera el código QR

- Asegúrate de que el microservicio esté corriendo correctamente
- Verifica el archivo `.env` con los datos necesarios

### ❌ No se sincronizan contactos

- Revisa permisos de modelo en `security/ir.model.access.csv`
- Asegúrate de que la sesión de WhatsApp esté activa

### ❌ Error al enviar mensajes

- Verifica el estado del cliente en consola
- Consulta logs en `./logs/`

---

## 📄 Registro de logs

Los logs se generan automáticamente por el microservicio de WhatsApp Web:

```
./logs/
└── wamo_2025-06-21.log
```

Incluyen autenticaciones, errores de conexión y mensajes enviados/recibidos.

---

## ⚠️ Limitaciones

- No utiliza la API oficial de WhatsApp Business (puede romperse si WhatsApp cambia su estructura)
- Requiere que el dispositivo esté conectado a internet y con la sesión activa
- No soporta múltiples usuarios simultáneos en la misma instancia (sin modificación adicional)

---

## 🤝 Contribución

¿Te interesa mejorar WAMO?

- 🐛 Reporta errores abriendo un issue
- ✨ Propón mejoras para nuevas versiones
- 🔧 Envía pull requests con parches o funciones nuevas

---

## 📄 Licencia

Este proyecto está bajo la Licencia Odoo Proprietary License v1.0 (OPL-1).
Solo puede ser utilizado en condiciones compatibles con los términos de Odoo.

---

**Desarrollado con ❤️ para mejorar la comunicación empresarial a través de WhatsApp y Odoo**

<div align="center">

**[⬆ Volver al inicio](#-wamo---whatsapp-message-app-for-odoo)**

</div>
