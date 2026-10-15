# AuraHash ID — Perfiles de Aplicación

> **Propósito:** definir los perfiles oficiales de AuraHash ID. Cada perfil es un "contrato" entre emisor, portador y lector: qué datos viajan, qué se cifra, qué se firma, qué se verifica.
>
> **Estado:** documento vivo. Los perfiles describen **visión completa**, con marcas explícitas de qué está **implementado hoy (v2.4.0)** vs qué es **feature futuro**.

---

## 1. Por qué perfiles (y no un solo formato)

AuraHash ID se aplica a dominios muy distintos: emergencias médicas, niños perdidos, eventos, contratos legales, industria. Forzar un único formato a todos sería un error de diseño: sobrecargaría casos simples y dejaría cortos a los complejos.

La solución es un **núcleo común** con **perfiles** que activan o desactivan bloques del payload según el caso de uso.

### Núcleo común (todos los perfiles)

- Data Matrix (ISO/IEC 16022) escaneable por Google Lens / WeChat.
- Aura Estocástica (SHA-256, determinista, anti-falsificación visual).
- Capa `PUB` en texto claro (JSON minificado con claves cortas).
- Bloque `SHA` con hash maestro truncado a 32 hex.

### Bloques opcionales según perfil

| Bloque | Descripción | Presente en |
|--------|-------------|-------------|
| `MED` | Capa médica cifrada (zlib + AES-256-GCM) | Salud |
| `ADM` | Capa administrativa cifrada | Salud, Legal (opcional) |
| `SIG` | Firma Ed25519 del payload | Todos (opcional) |
| `URL` | Endpoint de verificación de estado | Verificación |

**Filosofía:** un solo motor (`generator.py`), un solo lector (`reader.py`), perfiles declarados vía campo `perfil` en el JSON de entrada.

---

## 2. Los 4 perfiles

### 2.1 — `Salud` (familia crítica)

**Objetivo:** proveer información médica vital a personal de emergencia sin depender de servidores.

**Casos de uso:**
- Pulsera de emergencia médica.
- Identificación de ciclista / motociclista accidentado.
- Adulto mayor con condiciones crónicas.
- Deportistas con alergias o condiciones.
- Identificación médica en cascos / vehículos.

**Contrato de bloques:**
```
PUB:{json_minificado}|MED:AES256GCMZ:{...}|ADM:AES256GCMZ:{...}|SHA:{32hex}|SIG:{b64}
```

**Actor emisor:** hospital, aseguradora, médico tratante.

**Actores lectores:**
- **Paramédico (ambulancia):** acceso inmediato a alergias, tipo de sangre, medicamentos críticos, instrucciones.
- **Médico tratante:** historial clínico completo.
- **Hospital:** datos administrativos de admisión.
- **Aseguradora:** póliza, cobertura, CURP parcial.

**Niveles de acceso (visión futura — RBAC):**

Hoy, `MED` y `ADM` comparten la misma llave AES: quien la tenga, descifra ambas. La **visión** es cifrado por rol con **envelope encryption**: cada capa tiene su propia DEK (Data Encryption Key), y cada rol recibe solo los sobres que le corresponden. Implementación pendiente.

**Estado actual (v2.4.0):** funcional end-to-end con llave AES compartida + firma Ed25519.

---

### 2.2 — `Contacto` (familia humanitaria)

**Objetivo:** reunir a una persona o mascota extraviada con su familia. **Todo público, cero cripto adicional.**

**Casos de uso:**
- Niño perdido (pulsera, mochila, calcomanía).
- Mascota extraviada (collar, placa).
- Adulto mayor sin condiciones críticas.
- Persona con discapacidad comunicativa (autismo, Alzheimer).

**Contrato de bloques:**
```
PUB:{json_minificado}|SHA:{32hex}|SIG:{b64}
```

**Sin `MED` ni `ADM`.** El objetivo es que **CUALQUIERA** — sin app, sin llave, sin conexión — pueda leer los datos y contactar a la familia. Google Lens basta.

**Actor emisor:** DIF, protectora de animales, familia directa, escuela.

**Actores lectores:** cualquier persona con un smartphone y Google Lens / WeChat.

**Firma Ed25519 (opcional):** permite verificar que el AuraHash fue emitido por una entidad legítima (ej: el DIF emitió esa pulsera, no un falsificador).

**Estado actual (v2.4.0):** funcional. Solo se necesita generar el escenario sin capas `MED`/`ADM`.

---

### 2.3 — `Verificacion` (familia de estado dinámico)

**Objetivo:** validar que un objeto, boleto o activo está **vigente AHORA**, no solo que es auténtico.

**Casos de uso:**
- Anti-reventa de boletos (boleto nominativo, Aura Dinámica cada 30s).
- Industria 4.0 (máquina operativa / en mantenimiento / fuera de servicio).
- Control de acceso físico (credencial vigente, permisos).
- Trazabilidad de activos en zonas remotas.
- Autenticación de lotes farmacéuticos (no revocado, no caducado).

**Contrato de bloques:**
```
PUB:{id, emisor, tipo, ...}|SHA:{32hex}|SIG:{b64}|URL:{endpoint_verificacion}
```

**Nota crítica:** este es el **único perfil que rompe el "offline-first"** en su forma completa. Saber si un boleto fue usado o si una máquina está operativa requiere consultar un estado global. La cripto aquí protege **autenticidad** (firma Ed25519) y, opcionalmente, **privacidad del ID**.

**Estrategia offline-first parcial:**
- El lector cachea localmente los estados recientes.
- Si no hay red, marca el escaneo como "pendiente de verificación" y sincroniza después.
- Para anti-reventa estricto (boleto de concierto), se requiere conexión o un protocolo de rotación temporal (Aura Dinámica).

**Estado actual (v2.4.0):** **no implementado.** Documentado como visión.

---

### 2.4 — `Legal` (familia de certificación)

**Objetivo:** certificar la integridad y autoría de un documento o acto jurídico. **Sin datos personales sensibles, sin estado remoto.**

**Casos de uso:**
- Contratos al calce (notariales, civiles, mercantiles).
- Certificaciones profesionales (títulos, cédulas).
- Autenticación de obra de arte / coleccionables.
- Pasaporte de producto (trazabilidad ESG, circularidad).
- Certificados de origen, calidad, sanitarios.
- Licencias oficiales (conducir, portar armas, operar maquinaria).
- Actas de asamblea, acuerdos de consejo, votaciones internas auditables.

**Contrato de bloques:**
```
PUB:{hash_documento, emisor, tipo_acto, fecha, partes}|SHA:{32hex}|SIG:{b64}
```

**Cómo funciona:**
1. Se calcula el `SHA-256` del documento completo (PDF, texto, imagen).
2. Ese hash va en `PUB`, **no el documento**.
3. El AuraHash se firma con `Ed25519` usando la llave privada del emisor (notario, abogado, certificador).
4. **Verificación pública:** cualquiera puede:
   - Recalcular el hash del documento y comparar con `PUB.hash_documento`.
   - Verificar la firma con la llave pública del emisor.
   - Confirmar que el documento no fue alterado desde su emisión.

**Ventajas frente a firma electrónica tradicional (Adobe, DocuSign, FIEL):**
- **Offline-first.** No depende de servidores del proveedor.
- **Verificable a perpetuidad.** Si el proveedor cierra, el AuraHash sigue funcionando.
- **Portable al mundo físico.** El mismo AuraHash puede ir impreso al calce de un contrato en papel.

**Actor emisor:** notario, despacho jurídico, autoridad certificadora, artista, fabricante.

**Actores lectores:** cualquier persona con la llave pública del emisor.

**Estado actual (v2.4.0):** **no implementado.** Documentado como visión.

---

## 3. Comparativa de perfiles

| Perfil | Confidencialidad | Estado remoto | Firma | Cifrado | Offline-first |
|--------|-----------------|---------------|-------|---------|---------------|
| **Salud** | Sí (RBAC futuro) | No | Sí | AES-256-GCM | 100% |
| **Contacto** | No (todo público) | No | Opcional | No | 100% |
| **Verificacion** | Parcial (ID opcional) | **Sí** | Sí | Opcional | Parcial |
| **Legal** | No (todo público) | No | Sí | No | 100% |

---

## 4. Otros escenarios aplicables (futuros)

Además de los 4 perfiles formales, AuraHash ID tiene aplicación en:

| Escenario | Perfil | Notas |
|-----------|--------|-------|
| Anti-falsificación de medicamentos | Verificacion | Lote farmacéutico firmado |
| Cadena de frío (alimentos, vacunas) | Verificacion | Registros firmados secuencialmente |
| Identificación de personal en obra | Salud | Híbrido con Verificacion |
| Historial veterinario de mascota | Salud (simplificado) | Contacto + alergias + vacunas |
| Trazabilidad de donaciones | Verificacion | Verificar destino |
| Licencias de conducir | Legal + Salud | Datos sensibles en capa privada |

**NO en scope (requiere investigación específica):**
- Voto electrónico ciudadano end-to-end verificable. Requiere ZK-proofs, mixnets, marco legal. Fuera del scope actual.

---

## 5. Formato del campo `perfil`

En el JSON de escenarios (`data/example_data.json`), cada escenario incluye:

```json
{
  "id": "salud_emergencia_01",
  "sector": "salud",
  "perfil": "salud",
  "capa_publica": { ... },
  "capa_medica": { ... },
  "capa_administrativa": { ... }
}
```

**Valores válidos:** `"salud"`, `"contacto"`, `"verificacion"`, `"legal"`.

**Retrocompatibilidad:** si el campo no está presente, se asume `"salud"` (formato histórico v2.x). Los lectores v1.3.0+ muestran el perfil detectado.

---

## 6. Estado de implementación (v2.4.0)

| Perfil | Formato | Generador | Reader | Notas |
|--------|---------|-----------|--------|-------|
| Salud | Definido | ✅ Funcional | ✅ Funcional | RBAC es feature futuro |
| Contacto | Definido | ✅ Funcional (sin MED/ADM) | ✅ Funcional | Firma opcional |
| Verificacion | Definido | ⏳ Pendiente | ⏳ Pendiente | Requiere estado remoto |
| Legal | Definido | ⏳ Pendiente | ⏳ Pendiente | Requiere hash de documento |

---

## 7. Roadmap por perfil

- **Salud:** RBAC con envelope encryption (llave por rol).
- **Contacto:** sin cambios estructurales. Solo documentar variantes.
- **Verificacion:** Aura Dinámica + endpoint de estado + cache offline.
- **Legal:** generador de AuraHash para documentos + verificación pública de hash.

---

*Última actualización: 2026-10-15 — Pendiente #12 (formalización de perfiles)*