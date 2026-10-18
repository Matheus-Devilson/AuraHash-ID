<div align="center">

# 🛡️ AuraHash ID

**El Protocolo Universal de Confianza Física-Digital.**

*Autenticación offline · Anti-falsificación visual · Privacidad por diseño*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Standard](https://img.shields.io/badge/ISO%2FIEC-16022%20Data%20Matrix-005571?style=flat-square)](https://www.iso.org/standard/44230.html)
[![Crypto](https://img.shields.io/badge/Crypto-AES--256--GCM%20%2B%20Ed25519-8A2BE2?style=flat-square)](https://ed25519.cr.yp.to/)
[![Status](https://img.shields.io/badge/Status-MVP%20v3.0.1-orange?style=flat-square)]()

</div>

---

> **¿Primera vez aquí?** Lee [`docs/VISION.md`](docs/VISION.md) para entender por qué AuraHash ID es diferente.
>
> **¿Buscas el speech para presentaciones?** Lee [`docs/VISION_COMERCIAL.md`](docs/VISION_COMERCIAL.md).
>
> **¿Buscas las limitaciones conocidas?** Lee [`docs/LIMITACIONES.md`](docs/LIMITACIONES.md).

>**¿Buscas una guia completa como se usa?** Lee[`docs/EJEMPLO_DE_USO.md`](docs/EJEMPLO_DE_USO.md) para una guía paso a paso.

---

## 📖 ¿Qué es AuraHash ID?

**AuraHash ID** es un protocolo criptográfico que vincula objetos físicos, personas y documentos con su identidad digital de forma **segura, offline y privada**.

Combina tres tecnologías:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 🔷 **Núcleo** | Data Matrix (ISO/IEC 16022) | Compatibilidad universal con lectores existentes (Google Lens, WeChat, cámaras nativas) |
| 🎨 **Seguridad Visual** | Aura Estocástica (SHA-256) | Patrón de ruido determinista anti-falsificación detectable a simple vista |
| 🔐 **Criptografía** | AES-256-GCM + Ed25519 | Confidencialidad de datos sensibles + firma digital verificable offline |

> **Filosofía central:** 100% Offline-First. Cero dependencia de servidores en el momento de la lectura. Privacidad por diseño.

---

## 🚀 ¿Por qué AuraHash ID?

En un mundo hiperconectado, depender de servidores para verificar la identidad física es un **punto único de falla**: caídas de red, hackeos, falta de señal.

AuraHash ID devuelve el control al **borde** (Edge Computing), llevando criptografía de grado bancario al mundo físico — **sin apps propietarias, sin internet, sin rastreo**.

---

## 🌍 Casos de Uso Universales

| Sector | Aplicación | Beneficio Clave |
|--------|-----------|-----------------|
| 🏥 **Salud y Emergencias** | Pulseras de pacientes, historiales críticos | Paramédicos leen tipo de sangre y alergias sin señal celular |
| 🏭 **Industria 4.0** | Trazabilidad de activos y maquinaria | Identificación en zonas remotas sin WiFi |
| 👶 **Seguridad Personal** | Identificación de niños y adultos mayores | Contacto de emergencia sin exponer datos sensibles |
| 🎟️ **Eventos y Accesos** | Boletos nominativos, control de acceso | Anti-reventa, validación en 0.2s, offline |
| 📜 **Documentos Legales** | Contratos, credenciales, certificados | Verificación de integridad sin servidor |
| 🚴 **Seguridad Vial** | Cascos, vehículos, identificación médica | Datos vitales en accidentes |
| ✈️ **Aviación Comercial** | Boletos, equipaje, emergencias en vuelo | Anti-reventa, abordaje offline, perfil salud embebido |
| 🎖️ **Militar y Defensa** | Identificación de tropa, órdenes cifradas, logística | Funciona donde todo lo demás falla: sin red, sin GPS, sin servidores |
| 🏛️ **Gobierno** | Identificación ciudadana, licencias, programas sociales | Soberanía tecnológica sin servidores extranjeros |
| 🐾 **Mascotas y Animales** | Identificación, historial veterinario | Verificable offline por cualquier veterinario |
| 🌍 **ONGs y Ayuda Humanitaria** | Refugiados, distribución de alimentos | Identidad verificable sin pasaporte ni backend |
| 💰 **Sector Financiero** | Tarjetas, cheques, contratos | Firma Ed25519 verificable offline |
| 🎨 **Autenticación de Productos** | Obras de arte, vinos, medicamentos, lujo | Anti-falsificación con certificado firmado |

### Caso destacado: Eventos (anti-reventa y control del emisor)

AuraHash ID convierte el boleto en un **activo controlado por el emisor** (modelo boleto aéreo):

- **Vinculación a INE:** el boleto lleva `SHA-256(INE + nombre)`. La INE nunca viaja en claro.
- **Anti-reventa:** sin la INE del titular original, el boleto no entra.
- **Verificación offline-first:** las pistolas del staff descargan una lista firmada antes del evento y funcionan sin red.
- **Verificación en 0.2s:** firma Ed25519 + hash de INE + estado del boleto.
- **Reembolso configurable:** el emisor define política (ventana, cargo por cancelación tardía).
- **Auditoría completa:** vendidos, cancelados, asistencia en tiempo real, intentos de fraude detectados.

### Caso destacado: Militar (donde todo lo demás falla)

En guerra, la conectividad es lo primero que se pierde. AuraHash ID funciona sin red, sin servidores, sin energía, sin GPS.

- **Identificación de tropa:** dog tags del siglo XXI. Capa pública + capa médica cifrada.
- **Órdenes cifradas:** firmadas con Ed25519 por el comandante. Verificables offline.
- **Logística:** trazabilidad total de suministros. Cada movimiento firmado.
- **Inteligencia:** documentos con capa pública señuelo y capa administrativa cifrada real.
- **MEDEVAC:** historial médico en 2 segundos. El médico de campo escanea y sabe qué hacer.
- **Comunicaciones:** mensajes cifrados sin radio. El enemigo intercepta y solo ve base64.

**Documentación detallada:**
- [`docs/VISION.md`](docs/VISION.md) — Visión universal y todos los sectores.
- [`docs/FLUJO_EVENTOS.md`](docs/FLUJO_EVENTOS.md) — Flujo end-to-end de eventos.
- [`docs/VISION_COMERCIAL.md`](docs/VISION_COMERCIAL.md) — Speech y Q&A para presentaciones.

---

## 🗂️ Arquitectura de Datos (3 Capas)

El payload se estructura en tres capas, cada una con distinto nivel de exposición y protección:

| Capa | Contenido | Protección | Visible con Google Lens |
|------|-----------|-----------|-------------------------|
| **`capa_publica`** | Nombre de pila, instrucción de emergencia, alergias críticas | **Texto claro** — JSON minificado con claves cortas | ✅ Sí |
| **`capa_medica`** | Tipo de sangre, condiciones, medicamentos, notas | **AES-256-GCM + zlib** + Ed25519 | ❌ No (solo cifrado) |
| **`capa_administrativa`** | Pólizas, CURP parcial, datos legales | **AES-256-GCM + zlib** + Ed25519 | ❌ No (solo cifrado) |

> La **capa pública nunca se cifra** porque es información de emergencia diseñada para ser leída al instante por un paramédico con cualquier smartphone.

---

## 🔐 Arquitectura de Seguridad

Basada en el **Principio de Kerckhoffs**: el sistema es seguro incluso si todo su diseño es público, porque la seguridad reside en las **llaves**.

### Capa 1 — Núcleo Criptográfico (SHA-256)

El "Aura" visual se genera usando SHA-256. Si un solo bit de los datos cambia, el 50% del patrón visual cambia (**Efecto Avalancha**).

### Capa 2 — Confidencialidad (AES-256-GCM + zlib)

- Capas **médica** y **administrativa** cifradas con **AES-256-GCM** (cifrado autenticado: confidencialidad + integridad).
- **zlib** aplicado ANTES de cifrar (reduce ~40% el tamaño del ciphertext).
- Clave maestra en `keys/aes.key` (32 bytes), **nunca** sube a git.
- **Nonce determinista**: derivado de `sha256(id_escenario + '::' + comprimido)[:12]`. Garantiza reproducibilidad.

### Capa 3 — Autenticidad (Ed25519)

- **Llave Privada** (`keys/ed25519_private.key`): firma el payload completo. **Nunca** sube a git.
- **Llave Pública** (`keys/ed25519_public.key`): verifica offline. **Sí** se distribuye en el repo.
- Firma: 64 bytes sobre el mensaje `PUB|MED|ADM|SHA` (excluye el bloque `SIG` para evitar recursión).

### Capa 4 — Resistencia Física

El Data Matrix usa corrección de errores **Reed-Solomon**, sobreviviendo hasta un 30% de daño (rayones, suciedad, humedad).

---

## 📦 Formato del Payload (v3.0.1)

    PUB:{json_minificado}|MED:AES256GCMZ:{base64}|ADM:AES256GCMZ:{base64}|SHA:{32hex}|SIG:{base64}

**Bloques:**

| Bloque | Descripción |
|--------|-------------|
| `PUB:` | JSON minificado con claves cortas (`p`, `t`, `i`, `n`, `a`, `v`, `e`). Texto claro. |
| `MED:` | Capa médica cifrada. Prefijo `AES256GCMZ:` = zlib + AES-256-GCM. |
| `ADM:` | Capa administrativa cifrada. Mismo esquema que `MED:`. |
| `SHA:` | SHA-256 maestro truncado a 32 hex (128 bits). |
| `SIG:` | Firma Ed25519 del mensaje `PUB|MED|ADM|SHA`, en base64 (64 bytes). |

**Prefijos de cifrado soportados por el reader:**

- `AES256GCMZ:` → zlib + AES-256-GCM (formato actual, v2.3.0+)
- `AES256GCM:`  → solo AES-256-GCM (formato legacy v2.1.0, retrocompatible)

**Retrocompatibilidad:** el reader acepta payloads sin `SIG:` (los marca como `formato legacy`) y sin zlib.

---

## ⚙️ Cómo Funciona

    ┌──────────────────┐
    │  Payload (JSON)  │  ← Datos de entrada (identidad, salud, activo)
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │  SHA-256 Hash    │  ← Huella criptográfica única (3 hashes + maestro)
    └────────┬─────────┘
             ▼
       ┌─────┴─────┐
       ▼           ▼
    ┌──────┐  ┌──────────┐
    │ Aura │  │Data Matrix│  ← Dos capas visuales independientes
    │(ruido)│  │  (datos)  │
    └──┬───┘  └────┬─────┘
       └─────┬─────┘
             ▼
    ┌──────────────────┐
    │  Imagen Final    │  ← Lista para imprimir o mostrar en pantalla
    └──────────────────┘

1. Se recibe un **payload** (JSON con 3 capas).
2. Se cifran `MED` y `ADM` con **zlib + AES-256-GCM**.
3. Se calcula el **SHA-256** de cada capa (texto plano) + maestro combinado.
4. Se firma el payload completo con **Ed25519**.
5. El hash maestro genera el **Aura** (ruido determinista).
6. El payload firmado se codifica en un **Data Matrix**.
7. Todo se fusiona en una imagen `.png`.

---

## 🛠️ Instalación y Uso

### Prerrequisitos

- Python **3.10+** (probado en 3.14.8)
- pip (gestor de paquetes de Python)

### Instalación

    # 1. Clonar el repositorio
    git clone https://github.com/Matheus-Devilson/AuraHash-ID.git
    cd AuraHash-ID

    # 2. (Recomendado) Crear entorno virtual
    python -m venv venv

    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate

    # 3. Instalar dependencias
    pip install -r requirements.txt

### Generar llaves (primera vez)

    # Clave AES-256 (32 bytes)
    python -c "import secrets, pathlib; pathlib.Path('keys').mkdir(exist_ok=True); pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))"

    # Par Ed25519 (privada + pública)
    python src/keys_manager.py

### Generar imágenes

    python src/generator.py

El script leerá `data/example_data.json` y generará 7 imágenes en `output/`.

### Leer un payload

    python src/reader.py

Pega el payload escaneado (una línea) y pulsa Enter. El reader:

- Descifra `MED` y `ADM` (soporta zlib y legacy).
- Reconstruye la capa pública legible.
- Verifica integridad SHA-256.
- Verifica firma Ed25519 (informativa, nunca bloquea).

**Para probar con tu celular:** abre una imagen generada y escanéala con Google Lens. Verás el payload en texto plano.

---

## 📱 PWA Reader (demo universal)

La PWA (`pwa/index.html`) permite leer un Data Matrix desde el navegador, descifrar las capas MED y ADM con AES-256-GCM, y verificar la firma Ed25519. **Todo offline, sin servidores.**

### Cómo usarla

    # 1. Iniciar servidor local en la carpeta pwa/
    cd pwa
    python -m http.server 8000

    # 2. Abrir en el navegador
    # http://localhost:8000

### Qué lee

| Escenario | zxing-js (PWA) | Google Lens | reader.py |
|-----------|----------------|-------------|-----------|
| salud_emergencia_02 | ✅ | ✅ | ✅ |
| personal_ciclista_01 | ✅ | ✅ | ✅ |
| evento_boleto_01 | ✅ | ✅ | ✅ |
| seguro_auto_01 | ✅ | ✅ | ✅ |
| contacto_nino_01 | ✅ | ✅ | ✅ |
| legal_contrato_02 | ⚠️ Puede fallar | ✅ | ✅ |
| militar_inteligencia_01 | ⚠️ Puede fallar | ✅ | ✅ |

### ⚠️ Limitación importante

**La PWA (zxing-js) funciona al ~70%.** Es una limitación de la librería JS, no del protocolo.

**Para el 100% de éxito:**
- **`reader.py` (Python)**: 100% funcional.
- **Google Lens**: 100% funcional (solo capa pública).
- **App nativa futura**: 100% (con SDK nativo).

**La PWA es una demo universal.** Para producción, se requiere una app nativa.

**Solución para producción**: usar un SDK nativo (Google ML Kit, Apple Vision, Dynamsoft) con tasas de éxito >95%.

### Archivos

- `pwa/index.html` — PWA completa (HTML + CSS + JS inline).
- `docs/LIMITACIONES.md` — Limitaciones de zxing-js.

---

## 📂 Estructura del Proyecto

    AuraHash-ID/
    ├── src/
    │   ├── generator.py         # Motor v3.0.1 (AES + zlib + Ed25519 + nonce determinista)
    │   ├── reader.py            # Lector/verificador v1.4.0
    │   └── keys_manager.py      # Generador de llaves Ed25519
    ├── data/
    │   └── example_data.json    # 7 escenarios
    ├── output/                  # Imágenes generadas (.png, ignoradas por git)
    ├── pwa/
    │   └── index.html           # PWA reader v2.0.1
    ├── keys/
    │   ├── aes.key              # Clave AES-256 (32 bytes, IGNORADA por git)
    │   ├── ed25519_private.key  # Llave privada Ed25519 (32 bytes, IGNORADA)
    │   ├── ed25519_public.key   # Llave pública Ed25519 (32 bytes, TRACKEADA)
    │   └── .gitkeep
    ├── docs/
    │   ├── AI_CONTEXT.md        # Briefing estático del proyecto
    │   ├── PERFILES.md          # Los 4 perfiles formalizados
    │   ├── FLUJO_EVENTOS.md     # Flujo end-to-end de eventos
    │   ├── VISION.md            # Visión universal y casos de uso
    │   ├── VISION_COMERCIAL.md  # Speech y Q&A para presentaciones
    │   ├── LIMITACIONES.md      # Limitaciones conocidas de zxing-js
    │   └── MINI-CONTEXTO_*.txt  # Históricos de contexto
    ├── backups/                 # Backups locales (ignorados por git)
    ├── .gitignore
    ├── LICENSE                  # Licencia MIT
    ├── README.md                # Este archivo
    └── requirements.txt

---

## 🧰 Stack Tecnológico

- **Python 3.14.8**
- **segno** — Generación de Data Matrix (ISO/IEC 16022)
- **numpy + Pillow** — Aura estocástica e imagen final
- **cryptography 50.0.2** — AES-256-GCM + Ed25519
- **zlib** (stdlib) — Compresión previa al cifrado
- **zxing-js 0.21.3** — Lector de Data Matrix en la PWA (CDN)
- **Web Crypto API** — Descifrado AES-GCM y verificación Ed25519 en la PWA
- **DecompressionStream** — Descompresión zlib nativa en la PWA

---

## 🗺️ Roadmap

- [x] Definición de arquitectura y visión universal
- [x] Estructura inicial del repositorio
- [x] Generador universal de payload (JSON → AuraHash)
- [x] Cifrado AES-256-GCM + zlib en capas sensibles
- [x] Firma digital Ed25519 end-to-end
- [x] Lector/verificador offline (`reader.py`)
- [x] Optimización del payload (-21.8% en v2.3.0)
- [x] Documento de visión universal (`docs/VISION.md`)
- [x] PWA Reader offline-first (demo universal)
- [x] Nonce determinista (reproducibilidad)
- [x] Documentación de limitaciones (`docs/LIMITACIONES.md`)
- [ ] SDK para integración en apps móviles (iOS/Android)
- [ ] Aura Dinámica para boletos digitales (rotación cada 30s)
- [ ] RBAC por rol (envelope encryption para perfil salud)
- [ ] Alianzas con fabricantes de pulseras y calcomanías industriales

---

## 📜 Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Matheus Devilson**
Creador y Arquitecto de AuraHash ID

[![GitHub](https://img.shields.io/badge/GitHub-Matheus--Devilson-181717?style=flat-square&logo=github)](https://github.com/Matheus-Devilson)

---

<div align="center">

**AuraHash ID** — *La confianza no debería depender de una conexión.*

</div>