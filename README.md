<div align="center">

# 🛡️ AuraHash ID

**El Protocolo Universal de Confianza Física-Digital.**

*Autenticación offline · Anti-falsificación visual · Privacidad por diseño*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Standard](https://img.shields.io/badge/ISO%2FIEC-16022%20Data%20Matrix-005571?style=flat-square)](https://www.iso.org/standard/44230.html)
[![Crypto](https://img.shields.io/badge/Crypto-AES--256--GCM%20%2B%20Ed25519-8A2BE2?style=flat-square)](https://ed25519.cr.yp.to/)
[![Status](https://img.shields.io/badge/Status-MVP%20v2.4.0-orange?style=flat-square)]()

</div>

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

### Caso destacado: Eventos (anti-reventa y control del emisor)

AuraHash ID convierte el boleto en un **activo controlado por el emisor** (modelo boleto aéreo):

- **Vinculación a INE:** el boleto lleva `SHA-256(INE + nombre)`. La INE nunca viaja en claro.
- **Anti-reventa:** sin la INE del titular original, el boleto no entra.
- **Verificación offline-first:** las pistolas del staff descargan una lista firmada antes del evento y funcionan sin red.
- **Verificación en 0.2s:** firma Ed25519 + hash de INE + estado del boleto.
- **Reembolso configurable:** el emisor define política (ventana, cargo por cancelación tardía).
- **Auditoría completa:** vendidos, cancelados, asistencia en tiempo real, intentos de fraude detectados.

**Documentación detallada:**
- [`docs/FLUJO_EVENTOS.md`](docs/FLUJO_EVENTOS.md) — Flujo end-to-end.
- [`docs/VISION_COMERCIAL.md`](docs/VISION_COMERCIAL.md) — Speech y Q&A para presentaciones.
---

## 🏗️ Arquitectura de Datos (3 Capas)

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

### Capa 3 — Autenticidad (Ed25519)

- **Llave Privada** (`keys/ed25519_private.key`): firma el payload completo. **Nunca** sube a git.
- **Llave Pública** (`keys/ed25519_public.key`): verifica offline. **Sí** se distribuye en el repo.
- Firma: 64 bytes sobre el mensaje `PUB|MED|ADM|SHA` (excluye el bloque `SIG` para evitar recursión).

### Capa 4 — Resistencia Física

El Data Matrix usa corrección de errores **Reed-Solomon**, sobreviviendo hasta un 30% de daño (rayones, suciedad, humedad).

---

## 📦 Formato del Payload (v2.4.0)

```
PUB:{json_minificado}|MED:AES256GCMZ:{base64}|ADM:AES256GCMZ:{base64}|SHA:{32hex}|SIG:{base64}
```

**Bloques:**

| Bloque | Descripción |
|--------|-------------|
| `PUB:` | JSON minificado con claves cortas (`t`, `i`, `n`, `a`, `v`, `e`). Texto claro. |
| `MED:` | Capa médica cifrada. Prefijo `AES256GCMZ:` = zlib + AES-256-GCM. |
| `ADM:` | Capa administrativa cifrada. Mismo esquema que `MED:`. |
| `SHA:` | SHA-256 maestro truncado a 32 hex (128 bits). |
| `SIG:` | Firma Ed25519 del mensaje `PUB\|MED\|ADM\|SHA`, en base64 (64 bytes). |

**Prefijos de cifrado soportados por el reader:**

- `AES256GCMZ:` → zlib + AES-256-GCM (formato actual, v2.3.0+)
- `AES256GCM:`  → solo AES-256-GCM (formato legacy v2.1.0, retrocompatible)

**Retrocompatibilidad:** el reader acepta payloads sin `SIG:` (los marca como `formato legacy`) y sin zlib.

---

## ⚙️ Cómo Funciona

```
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
```

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

```bash
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
```

### Generar llaves (primera vez)

```bash
# Clave AES-256 (32 bytes)
python -c "import secrets, pathlib; pathlib.Path('keys').mkdir(exist_ok=True); pathlib.Path('keys/aes.key').write_bytes(secrets.token_bytes(32))"

# Par Ed25519 (privada + pública)
python src/keys_manager.py
```

### Generar imágenes

```bash
python src/generator.py
```

El script leerá `data/example_data.json` y generará 4 imágenes en `output/`.

### Leer un payload

```bash
python src/reader.py
```

Pega el payload escaneado (una línea) y pulsa Enter. El reader:

- Descifra `MED` y `ADM` (soporta zlib y legacy).
- Reconstruye la capa pública legible.
- Verifica integridad SHA-256.
- Verifica firma Ed25519 (informativa, nunca bloquea).

**Para probar con tu celular:** abre una imagen generada y escanéala con Google Lens. Verás el payload en texto plano.

---

## 📂 Estructura del Proyecto

```
AuraHash-ID/
├── src/
│   ├── generator.py         # Motor v2.4.0 (AES-256-GCM + zlib + Ed25519)
│   ├── reader.py            # Lector/verificador v1.3.0
│   └── keys_manager.py      # Generador de llaves Ed25519
├── data/
│   └── example_data.json    # 4 escenarios (texto plano legible)
├── output/                  # Imágenes generadas (.png, ignoradas por git)
├── keys/
│   ├── aes.key              # Clave AES-256 (32 bytes, IGNORADA por git)
│   ├── ed25519_private.key  # Llave privada Ed25519 (32 bytes, IGNORADA)
│   ├── ed25519_public.key   # Llave pública Ed25519 (32 bytes, TRACKEADA)
│   └── .gitkeep
├── docs/                    # Documentación y mini-contextos
├── backups/                 # Backups locales (ignorados por git)
├── .gitignore
├── LICENSE                  # Licencia MIT
├── README.md                # Este archivo
└── requirements.txt
```

---

## 🧰 Stack Tecnológico

- **Python 3.14.8**
- **segno** — Generación de Data Matrix (ISO/IEC 16022)
- **numpy + Pillow** — Aura estocástica e imagen final
- **cryptography 50.0.2** — AES-256-GCM + Ed25519
- **zlib** (stdlib) — Compresión previa al cifrado

---

## 🗺️ Roadmap

- [x] Definición de arquitectura y visión universal
- [x] Estructura inicial del repositorio
- [x] Generador universal de payload (JSON → AuraHash)
- [x] Cifrado AES-256-GCM + zlib en capas sensibles
- [x] Firma digital Ed25519 end-to-end
- [x] Lector/verificador offline (`reader.py`)
- [x] Optimización del payload (-21.8% en v2.3.0)
- [ ] SDK para integración en apps móviles (iOS/Android)
- [ ] Aura Dinámica para boletos digitales (rotación cada 30s)
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