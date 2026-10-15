<div align="center">

# 🛡️ AuraHash ID

**El Protocolo Universal de Confianza Física-Digital.**

*Autenticación offline · Anti-falsificación visual · Privacidad por diseño*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Standard](https://img.shields.io/badge/ISO%2FIEC-16022%20Data%20Matrix-005571?style=flat-square)](https://www.iso.org/standard/44230.html)
[![Crypto](https://img.shields.io/badge/Crypto-AES--256--GCM%20%2B%20Ed25519-8A2BE2?style=flat-square)](https://ed25519.cr.yp.to/)
[![Status](https://img.shields.io/badge/Status-MVP%20v2.4.1-orange?style=flat-square)]()

</div>

---

> **¿Primera vez aquí?** Lee [`docs/VISION.md`](docs/VISION.md) para entender por qué AuraHash ID es diferente.
>
> **¿Buscas el speech para presentaciones?** Lee [`docs/VISION_COMERCIAL.md`](docs/VISION_COMERCIAL.md).

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

### Capa 3 — Autenticidad (Ed25519)

- **Llave Privada** (`keys/ed25519_private.key`): firma el payload completo. **Nunca** sube a git.
- **Llave Pública** (`keys/ed25519_public.key`): verifica offline. **Sí** se distribuye en el repo.
- Firma: 64 bytes sobre el mensaje `PUB|MED|ADM|SHA` (excluye el bloque `SIG` para evitar recursión).

### Capa 4 — Resistencia Física

El Data Matrix usa corrección de errores **Reed-Solomon**, sobreviviendo hasta un 30% de daño (rayones, suciedad, humedad).

---

## 📦 Formato del Payload (v2.4.1)
