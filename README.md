<div align="center">

# 🛡️ AuraHash ID

**El Protocolo Universal de Confianza Física-Digital.**

*Autenticación offline · Anti-falsificación visual · Privacidad por diseño*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Standard](https://img.shields.io/badge/ISO%2FIEC-16022%20Data%20Matrix-005571?style=flat-square)](https://www.iso.org/standard/44230.html)
[![Crypto](https://img.shields.io/badge/Crypto-Ed25519-8A2BE2?style=flat-square)](https://ed25519.cr.yp.to/)
[![Status](https://img.shields.io/badge/Status-Early%20Development-orange?style=flat-square)]()

</div>

---

## 📖 ¿Qué es AuraHash ID?

**AuraHash ID** es un estándar criptográfico que vincula objetos físicos, personas y documentos con su identidad digital de forma **segura, offline y privada**.

Combina tres capas de tecnología:

| Capa | Tecnología | Función |
|------|-----------|---------|
| 🔷 **Núcleo** | Data Matrix (ISO/IEC 16022) | Compatibilidad universal con lectores existentes (Google Lens, WeChat, cámaras nativas) |
| 🎨 **Seguridad Visual** | Aura Estocástica (SHA-256) | Patrón de ruido determinista anti-falsificación detectable a simple vista |
| 🔐 **Criptografía** | Firma Digital (Ed25519) | Autenticidad matemática verificable sin conexión a internet |

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

---

## 🛡️ Arquitectura de Seguridad (4 Capas)

Basada en el **Principio de Kerckhoffs**: el sistema es seguro incluso si todo su diseño es público, porque la seguridad reside en la **Llave Privada**.

### Capa 1 — Núcleo Criptográfico (SHA-256)
El "Aura" visual se genera usando SHA-256. Si un solo bit de los datos cambia, el 50% del patrón visual cambia (**Efecto Avalancha**).

### Capa 2 — Firma Digital Asimétrica (Ed25519)
- **Llave Privada:** Vive exclusivamente en un HSM (Hardware Security Module) del emisor (hospital, fábrica, empresa). **Nunca sale del servidor.**
- **Llave Pública:** Se distribuye a los lectores offline. Solo permite **verificar**, no generar.

### Capa 3 — Validación Offline
Los lectores (Google Lens, apps de guardia, escáneres de campo) solo requieren la **Llave Pública** y la lista de hashes válidos del día. Cero dependencia de servidores.

### Capa 4 — Resistencia Física
El Data Matrix usa corrección de errores **Reed-Solomon**, sobreviviendo hasta un 30% de daño (rayones, suciedad, humedad).

---

## ⚙️ Cómo Funciona

```
┌──────────────────┐
│  Payload (JSON)  │  ← Datos de entrada (identidad, salud, activo)
└────────┬─────────┘
         ▼
┌──────────────────┐
│  SHA-256 Hash    │  ← Huella criptográfica única
└────────┬─────────┘
         ▼
   ┌─────┴─────┐
   ▼           ▼
┌──────┐  ┌────────────┐
│ Aura │  │ Data Matrix│  ← Dos capas visuales independientes
│(ruido)│ │  (datos)   │
└──┬───┘  └─────┬──────┘
   └─────┬──────┘
         ▼
┌──────────────────┐
│  Imagen Final    │  ← Lista para imprimir o mostrar en pantalla
└──────────────────┘
```

1. Se recibe un **payload** (JSON con los datos).
2. Se calcula el **hash SHA-256** del payload.
3. El hash se usa como **semilla** para generar el Aura (ruido determinista).
4. El payload se codifica en un **Data Matrix** legible universalmente.
5. Ambos se fusionan en una imagen `.png`.

---

## 🛠️ Instalación y Uso

### Prerrequisitos

- Python **3.8+**
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

### Uso

```bash
python src/generator.py
```

El script leerá `data/example_data.json` y generará las imágenes en `output/`.

**Para probar con tu celular:** abre la imagen generada y escanéala con Google Lens. Verás el payload en texto plano.

---

## 📂 Estructura del Proyecto

```
AuraHash-ID/
├── src/                     # Código fuente Python
│   └── generator.py         # Motor criptográfico y visual
├── data/                    # Datos de entrada (JSON)
│   └── example_data.json    # 4 escenarios de ejemplo
├── output/                  # Imágenes generadas (.png)
├── docs/                    # Documentación, diagramas, imágenes
├── keys/                    # ⚠️ Llaves privadas (NUNCA se suben)
├── .gitignore               # Protección de secretos
├── LICENSE                  # Licencia MIT
├── README.md                # Este archivo
└── requirements.txt         # Dependencias Python
```

---

## 🗺️ Roadmap

- [x] Definición de arquitectura y visión universal
- [x] Estructura inicial del repositorio
- [ ] Generador universal de payload (JSON → AuraHash)
- [ ] Implementación de firma digital Ed25519
- [ ] Módulo de verificación offline (lector)
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
