# AuraHash ID — Flujo completo de Eventos

> **Propósito:** describir end-to-end cómo se aplicaría AuraHash ID al sector eventos (conciertos, deportes, festivales, teatro). Documento de referencia técnica. NO es un pitch de venta.
>
> **Estado:** visión. Algunos componentes ya existen (`generator.py`, `reader.py`, cripto), otros son features futuros (app de staff, listas firmadas offline, integración con backend del promotor).

---

## 1. Principio rector

**El boleto es un activo controlado por el emisor, no propiedad absoluta del comprador.**

El comprador posee el boleto temporalmente. El emisor (Promotor de espectaulos) mantiene:

- La potestad de **cancelarlo** (si hay reembolso).
- La potestad de **re-emitirlo** a otro comprador.
- La potestad de **invalidarlo** (fraude).
- El **estado en tiempo real** (vendido, usado, cancelado, transferido).

**Analogía:** el boleto aéreo. Tú compras el asiento, pero la aerolínea controla la reserva. Si cancelas, ella reasigna el asiento.

---

## 2. Actores

| Actor | Rol |
|-------|-----|
| **Promotor** | Promotora de espctaculos, venue independiente |
| **Comprador** | Ana, quiere ver a su artista favorito |
| **Revendedor** | Formal o informal (el problema a mitigar) |
| **Staff de acceso** | El de la fila, con pistola digital |
| **Supervisor** | Backstage, resuelve conflictos |
| **Auditor** | Post-evento, revisa métricas |

---

## 3. Fase 1 — Promoción (antes de la venta)

### 3.1 — Pósters físicos en la calle

- Póster impreso con imagen del artista + fecha + venue.
- **Data Matrix** en una esquina con AuraHash de "anuncio oficial".
- **Contenido:**
  - `perfil: verificacion`
  - `tipo: EVENTO_ANUNCIO`
  - `evento`, `fecha`, `venue`, `ciudad`
  - `url_oficial: https://odesa.mx/nova`
  - `emisor: Promotra de espectaculos`
  - Firma Ed25519 de Promotora de Espectaculos
- **Función:**
  - Verificar que el anuncio es oficial (no fake).
  - Redirigir a la web de venta oficial.

### 3.2 — Pósters digitales (Facebook, Twitter, Instagram, WhatsApp)

- Mismo Data Matrix, mismo contenido.
- **Problema:** las plataformas recomprimen imágenes (Facebook baja resolución, Instagram degrada, Twitter recodifica).
- **Solución:** Data Matrix de **baja densidad** (poco payload) con **corrección de errores alta** (Reed-Solomon nivel H). El payload lleva solo lo esencial: ID + URL.
- **Alternativa:** en anuncios digitales, usar un QR simple con URL. El AuraHash completo va en el boleto, no en el anuncio.

### 3.3 — Televisión / YouTube

- El Data Matrix aparece 5-10 segundos en pantalla.
- **Problema:** el usuario tendría que escanear desde el sillón. Poco práctico.
- **Solución recomendada:** **NO usar AuraHash en TV**. Usar URL clara (`odesa.mx/nova`) o QR simple.
- **AuraHash en TV solo tiene sentido** si hay una app que captura el frame (complejo, fuera de scope).

---

## 4. Fase 2 — Compra del boleto

### 4.1 — Compra digital (web/app)

1. Ana entra a `pagpromotora.mx/evento`.
2. Selecciona evento, sección, asiento.
3. Introduce su INE: número + nombre completo.
4. El sistema le **muestra la política de reembolso** antes del pago.
5. Ana acepta.
6. Paga (tarjeta, SPEI, OXXO).
7. **Sistema emisor (Promotora de eventos):**
   - Genera `id_boleto` único (UUID).
   - Calcula `titular_hash = SHA-256(INE + nombre)`.
   - Aplica un AuraHash con:
     - `perfil: verificacion`
     - `tipo: BOLETO_EVENTO`
     - `id_boleto`
     - `evento, seccion, asiento, fecha_evento, venue`
     - `titular_hash` (NO la INE en claro)
     - `politica_reembolso` (ver sección 5)
     - `folio`
     - Firma Ed25519 de Promotora de eventos
8. Ana recibe:
   - Boleto digital (PDF con Data Matrix).
   - Opción de imprimir en físico.
   - Opción de añadir a Apple Wallet / Google Wallet (con Aura Dinámica futura).

**Privacidad clave:** la INE de Ana **no viaja en el payload**. Solo viaja un hash que permite verificar que el portador la conoce, sin revelarla.

### 4.2 — Compra física (taquilla, OXXO, farmacia)

1. Ana va a la taquilla.
2. Da su INE al cajero.
3. Cajero introduce INE + datos en el sistema.
4. Ana acepta la política de reembolso.
5. Paga.
6. **Sistema emisor imprime boleto físico** con:
   - Data Matrix con AuraHash completo.
   - Zona visible: nombre parcial, evento, sección, asiento, folio, política de reembolso.
   - **NO incluye la INE completa** (solo "Titular: Ana E***, INE verificada").
7. Ana se va con boleto físico + su INE.

---

## 5. Política de reembolso (configurable por el emisor)

**Principio:** AuraHash **no define la política**. La transporta en el payload, firmada por el emisor. El comprador la acepta al comprar.

**Estructura:**

```json
"politica_reembolso": {
  "permite": true,
  "modalidad": "flexible",
  "costo_adicional_mxn": 100,
  "ventana_gratis_horas": 48,
  "ventana_pago_hasta_minutos": 15,
  "nota": "Unico e intransferible. Reembolso gratis hasta 48h antes. Despues, hasta 15 min antes con cargo de $ MXN."
}
```

**Campos:**

| Campo | Descripción |
|-------|-------------|
| `permite` | ¿Se puede reembolsar? |
| `modalidad` | `no_reembolsable` / `estricta` / `flexible` / `siempre` |
| `costo_adicional_mxn` | Cargo por cancelación tardía. 0 si gratis. |
| `ventana_gratis_horas` | Horas antes del evento para reembolso gratis. |
| `ventana_pago_hasta_minutos` | Minutos antes del evento para reembolso con cargo. |
| `nota` | Texto humano mostrado al comprador. |

**Escenarios típicos:**

- **No reembolsable:** `{"permite": false, "modalidad": "no_reembolsable"}`.
- **Estricta (48h):** `{"permite": true, "modalidad": "estricta", "ventana_gratis_horas": 48}`.
- **Flexible (48h gratis + últimos 15 min con cargo):** ver arriba.
- **Siempre reembolsable:** `{"permite": true, "modalidad": "siempre", "costo_adicional_mxn": 0}`.

---

## 6. Ventana de cancelación y refresh de pistolas

**Regla clave:** la cancelación se cierra **T-15min** antes del evento. Después de ese corte, ya no se aceptan reembolsos.

**Razón técnica:** las pistolas de acceso descargan una **lista firmada** con el estado de los boletos. El refresh tarda unos minutos. T-15min da margen para que todas las pistolas tengan la última versión.

**Ciclo típico:**

| Momento | Acción |
|---------|--------|
| T-24h | Pistolas descargan lista completa firmada |
| T-6h | Refresh |
| T-1h | Refresh |
| T-30min | Refresh |
| **T-15min** | **Último refresh. Corte de cancelaciones.** |
| T-0 | Evento inicia |

**Durante el evento:** las pistolas operan con la lista local. Si no hay red, siguen funcionando (offline-first).

---

## 7. Fase 3 — Reventa y falsificaciones

### 7.1 — El problema

Ana no puede ir. Publica el boleto en Facebook Marketplace. Un estafador:
- Vende copias del mismo boleto a 3 personas.
- Cada comprador cree tener el boleto legítimo.

**Con AuraHash tradicional (payload estático):** los 3 compradores tienen el mismo Data Matrix. Todos ven `FIRMA OK`. Pero **solo el primero pasa** (el sistema marca el boleto como usado). Los otros 2 son rechazados — pero ya fueron estafados.

### 7.2 — Cómo AuraHash + INE resuelve

**El boleto lleva `titular_hash = SHA-256(INE + nombre)` desde su emisión.**

En la entrada:
- Staff escanea el Data Matrix.
- Sistema verifica firma Ed25519 (boleto legítimo).
- Pide la INE del portador.
- Calcula `SHA-256(INE + nombre)`.
- Compara con `titular_hash`.
- **Coincide:** acceso.
- **No coincide:** "Este boleto no es suyo."

**Resultado:**
- Ana (compradora original) puede entrar con su INE.
- El revendedor puede tener el Data Matrix, pero **no puede falsificar la INE**.
- Copias fraudulentas → rechazadas.

**Esto NO acaba con toda la reventa**, pero la vuelve inútil sin la INE original.

### 7.3 — Reventa oficial (controlada por el promotor)

El promotor puede habilitar **transferencia oficial:**

1. Ana entra a su cuenta Promotoria de eventos, libera el boleto.
2. Otro usuario lo reclama.
3. **Se re-emite con su propio `titular_hash`.**
4. El boleto original queda invalidado en el sistema.
5. El nuevo boleto tiene un AuraHash distinto.

**Esto sí acaba con la reventa informal.** El único camino legítimo de transferencia es el oficial.

---

## 8. Fase 4 — Ingreso al evento

### 8.1 — Flujo físico (boleto impreso + INE)

1. Ana llega a la fila.
2. Staff tiene pistola digital (lector de Data Matrix + terminal).
3. Ana presenta:
   - Boleto físico con Data Matrix.
   - INE física.
4. Staff escanea el Data Matrix.
5. La pistola lee el payload y muestra:
   - Nombre parcial: "Ana E***".
   - Sección A, asiento 4.
   - Evento: ej:NOVA Eclipse Tour.
   - Firma Ed25519: OK (boleto legítimo).
   - Estado: válido (no usado, no cancelado).
6. Staff escanea la INE de Ana (o introduce número).
7. La pistola calcula `SHA-256(INE + nombre)` y compara con `titular_hash`.
8. **Match:** acceso concedido.
9. La pistola marca el boleto como **usado** localmente.
10. **Tiempo total:** 0.2-0.5 segundos.

### 8.2 — Verificación offline

**Escenario:** el venue tiene mala señal. La pistola no se conecta al backend.

**Solución offline-first:**

- **Antes del evento:** el promotor descarga a cada pistola una **lista firmada de IDs de boletos válidos**.
- **Durante el evento (offline):**
  - La pistola escanea el Data Matrix.
  - Verifica la firma Ed25519 del boleto (offline).
  - Verifica que el ID está en la lista local (offline).
  - Verifica `titular_hash` contra la INE (offline).
  - Marca el boleto como usado **localmente**.
- **Después del evento:** la pistola sincroniza y sube la lista de boletos usados.

**Ventaja:** funciona 100% sin red.

**Limitación:** si dos pistolas offline aceptan el mismo boleto por 2 puertas distintas, se resuelve con:
- Consolidación por WiFi local del venue (no internet, solo red interna).
- O validación secundaria en la segunda puerta.

---

## 9. Fase 5 — Auditoría post-evento

| Métrica | Fuente |
|---------|--------|
| Boletos vendidos (físicos) | Registro de emisión |
| Boletos vendidos (digitales) | Registro de emisión |
| Boletos reembolsados | Registro de cancelaciones |
| **Ingresos por cargo de cancelación** | Suma de `costo_adicional_mxn` × cancelaciones tardías |
| Boletos transferidos | Registro de transferencias |
| Asistencia oficial en tiempo real | Boletos marcados como USADO |
| Recaudación por sección | Ventas × precio |
| **Intentos de ingreso falso** | Boletos rechazados por firma, hash, cancelación, uso duplicado |
| Hora pico de ingreso | Timestamps |
| Puertas con más rechazos | Detección de puertas problemáticas |
| Distribución geográfica (opcional) | Por código postal de INE |

**Todos estos datos son consecuencia natural de la arquitectura.** El AuraHash es el punto de verificación; el backend agrega las métricas.

---

## 10. Componentes técnicos

| Componente | ¿Existe hoy? | Comentario |
|------------|--------------|------------|
| Boleto con AuraHash firmado | ✅ Sí | `generator.py` |
| Data Matrix legible por pistola | ✅ Sí | ISO/IEC 16022 |
| Verificación de firma Ed25519 | ✅ Sí | `reader.py` |
| Campo `titular_hash` en payload | ✅ Trivial | Es un campo más |
| Campo `politica_reembolso` | ✅ Trivial | Es un campo más |
| Perfil `verificacion` completo | ⏳ Pendiente | Definido en `PERFILES.md` |
| App de staff | ❌ Feature futuro | Móvil o firmware de pistola |
| Verificación de INE (hash) | ❌ Feature futuro | Requiere integración con lector de INE |
| Lista firmada offline | ❌ Feature futuro | Protocolo nuevo |
| Backend del promotor | ❌ Responsabilidad del promotor | No es de AuraHash |

---

## 11. Diferenciación frente a soluciones existentes

| Modelo | Control del emisor | Revendible | Offline |
|--------|-------------------|------------|---------|
| Boleto físico tradicional | ❌ No | ✅ Sí | ✅ Sí |
| Boleto digital estático (QR) | Parcial | ✅ Sí | ✅ Sí |
| Boleto nominativo con ID (avión) | ✅ Sí | ❌ No | ❌ Requiere red |
| **AuraHash + INE + lista firmada** | **✅ Sí** | **❌ No** | **✅ Sí** |

**AuraHash combina lo mejor:** control del emisor (como avión) + offline-first (como boleto físico).

---

## 12. Lo que falta construir

### Por parte de AuraHash ID
1. Perfil `verificacion` completo.
2. Campos nuevos: `titular_hash`, `politica_reembolso`, `estado`.
3. App de staff (móvil o firmware).
4. Protocolo de lista firmada offline.
5. Aura Dinámica para wallet móvil.

### Por parte del promotor
1. Backend con base de datos de boletos + estados.
2. Sistema de venta vinculado a INE.
3. Sistema de transferencia oficial.
4. Sistema de emisión de listas firmadas.
5. Sistema de auditoría y reportes.

### Por parte del staff
1. Pistola compatible con Data Matrix + Ed25519.
2. App que verifica AuraHash.

---

*Última actualización: 2026-10-15 — Pendiente #13 (flujo de eventos)*
