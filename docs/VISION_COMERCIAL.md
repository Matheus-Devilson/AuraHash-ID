# AuraHash ID — Visión Comercial (Speech y Q&A)

> **Propósito:** este documento NO es un pitch de venta ni una propuesta comercial formal. Es un **speech de presentación** pensado para un auditorio con empresarios, promotores y tomadores de decisiones. Anticipa preguntas, responde objeciones, y explica el valor de AuraHash ID en el sector eventos.
>
> **Estado:** visión. AuraHash ID es un protocolo abierto (MIT). Lo que se presenta aquí es lo que un promotor podría construir sobre él.

---

## 1. El discurso de apertura (60 segundos)

> "Imaginen por un segundo la fila de entrada a un concierto. Miles de personas. El staff revisa boletos. Alguien llega con un boleto impreso. El staff lo mira, revisa el código, mira la foto, duda... ¿es legítimo? ¿ya entró alguien con este mismo boleto? ¿y si es una copia? En esa duda, se pierden 20 segundos por persona. 20 segundos × 5000 personas = 28 horas de fila. Y aún así, el fraude pasa.
>
> AuraHash ID elimina esa duda. En 0.2 segundos, la pistola del staff verifica:
> - Que el boleto fue emitido por el organizador oficial.
> - Que corresponde a la INE de quien lo presenta.
> - Que no ha sido usado, cancelado ni transferido.
> - Todo esto **sin necesidad de internet**.
>
> Y si alguien intentó revender el boleto sin permiso, el sistema lo detecta. Si alguien lo canceló y la empresa lo re-vendió, el sistema lo sabe. Si alguien intentó entrar con una copia, el sistema lo registra.
>
> No es magia. Es criptografía aplicada al mundo físico. Y hoy les voy a explicar cómo funciona y cómo podrían implementarlo en su empresa."

---

## 2. El problema (lo que duele hoy)

### 2.1 — Fraude de boletos

- **Copias físicas.** Un boleto fotocopiado 3 veces, vendido a 3 personas distintas.
- **QR clonados.** Boleto digital compartido por WhatsApp o Facebook. Todos creen tener el legítimo.
- **Falsificaciones.** Boletos "oficiales" impresos por terceros con logos robados.

### 2.2 — Reventa informal

- **Sobreprecio.** El revendedor compra a $1000, vende a $5000. La empresa no ve ese dinero.
- **Estafas.** El revendedor vende el mismo boleto a múltiples compradores.
- **Pérdida de control.** La empresa no sabe quién asiste al evento hasta que se sienta en el asiento.

### 2.3 — Operación en la fila

- **Verificación lenta.** El staff duda, revisa foto, compara nombre. 20 segundos por persona.
- **Dependencia de red.** Si la red cae, el sistema falla. Todo se detiene.
- **Poca auditoría.** Al final del evento, no se sabe cuántos boletos fueron falsos o cuántos intentos de ingreso se rechazaron.

### 2.4 — Protección de datos

- **Datos sensibles en el boleto.** Algunos sistemas imprimen nombre completo + CURP + dirección.
- **Cumplimiento legal.** Las leyes de protección de datos (LFPDPPP en México, GDPR en EU) exigen minimización de datos.

---

## 3. La solución AuraHash ID

### 3.1 — El boleto como activo controlado por el emisor

**Principio central:** el boleto es **tuyo mientras tú lo tengas**, pero **yo (el emisor) controlo el estado**. Igual que un boleto de avión.

**¿Qué significa esto en la práctica?**
- Tú puedes comprar el boleto. Pero no puedes venderlo sin mi permiso.
- Si cancelas, yo cancelo el boleto y lo re-vendo.
- Si alguien intenta falsificarlo, el sistema lo detecta.
- Si alguien intenta revenderlo, el sistema lo detecta.

### 3.2 — Cómo funciona (en 4 pasos)

1. **Emisión.** Al vender un boleto, el sistema genera un código AuraHash firmado digitalmente con la llave privada del organizador. Ese código se imprime en el boleto (como un Data Matrix) o se envía digitalmente.

2. **Vinculación.** El AuraHash contiene un hash criptográfico de la INE del comprador. **La INE no viaja en el boleto.** Solo el hash. Nadie puede reconstruir la INE desde el boleto.

3. **Verificación.** En la entrada, el staff escanea el código con una pistola. La pistola:
   - Verifica la firma digital del organizador (autenticidad).
   - Verifica que el hash de la INE coincida con el del portador.
   - Verifica que el boleto no esté cancelado ni usado.
   - Todo esto en 0.2 segundos, **sin internet**.

4. **Auditoría.** Después del evento, el organizador tiene métricas completas: boletos vendidos, cancelados, asistencia, fraudes detectados, intentos rechazados.

### 3.3 — Qué gana el organizador

| Problema hoy | AuraHash ID |
|--------------|-------------|
| Boletos fotocopiados | Hash vinculado a INE. No sirve la copia. |
| QR clonados | Firma digital. No sirve el clon. |
| Reventa informal | Sin INE del titular, no entra. |
| Fila lenta | 0.2 segundos por persona. |
| Dependencia de red | Offline-first. Funciona sin internet. |
| Sin auditoría | Métricas completas post-evento. |
| Datos sensibles expuestos | INE nunca viaja en claro. |

### 3.4 — Qué gana el comprador

- **Confianza.** Sabe que su boleto es legítimo.
- **Privacidad.** Su INE no está expuesta en el boleto.
- **Flexibilidad.** Puede reembolsar según la política que el organizador defina.
- **Protección.** No puede ser estafado por revendedores informales.

---

## 4. Preguntas frecuentes (Q&A del auditorio)

### 4.1 — ¿Esto reemplaza a Ticketmaster / ODESA?

**No.** AuraHash ID es un **protocolo de verificación**. Ticketmaster / ODESA seguirían siendo los emisores y dueños de la relación con el cliente. AuraHash es la capa criptográfica que agrega verificación y anti-reventa.

### 4.2 — ¿Qué pasa si el venue no tiene internet?

**Es exactamente el punto.** AuraHash es **offline-first**. Las pistolas descargan una lista firmada antes del evento y funcionan sin red. Si no hay red en el venue, nada se detiene.

### 4.3 — ¿Es obligatorio vincularlo a la INE?

**No.** Es configurable. El organizador puede:
- Exigir INE (máxima seguridad).
- Permitir otros documentos (pasaporte, licencia).
- No vincular a documento (boleto anónimo, pero entonces no hay anti-reventa).

### 4.4 — ¿Y si alguien pierde su INE?

El organizador puede definir una política de reemplazo. En general:
- Si es robada y hay denuncia, se puede re-emitir.
- Si es pérdida simple, depende de la política del organizador.

### 4.5 — ¿Cuánto cuesta implementarlo?

AuraHash ID es **código abierto MIT**. No hay costo de licencia del protocolo. Los costos reales son:
- Integración con el sistema del organizador (desarrollo).
- Pistolas digitales con capacidad de leer Data Matrix + verificar Ed25519.
- Capacitación del staff.
- Posible soporte y mantenimiento.

### 4.6 — ¿Es legal vincular un boleto a la INE?

Depende de la jurisdicción. En México:
- La INE es un documento de identificación oficial.
- El uso de la INE para verificación de identidad en eventos **no está prohibido**, pero debe cumplir con la LFPDPPP (Ley Federal de Protección de Datos Personales en Posesión de los Particulares).
- AuraHash **minimiza los datos**: solo guarda un hash, no la INE completa. Esto ayuda al cumplimiento.
- **Recomendación:** asesoría legal específica por jurisdicción.

### 4.7 — ¿Qué pasa si alguien quiere regalar el boleto a un amigo?

Depende de la política del organizador:
- **Transferencia oficial:** el organizador permite transferir vía su sistema. El boleto se re-emite con el hash del nuevo titular.
- **No transferible:** el boleto solo funciona con la INE del comprador original.

### 4.8 — ¿Cómo se evita que dos personas entren con el mismo boleto?

Porque:
- El boleto está vinculado a **una INE**.
- Al entrar, la pistola verifica el `SHA-256(INE + nombre)`.
- Si dos personas distintas lo presentan, solo una tendrá la INE correcta.
- El sistema marca el boleto como **usado** en cuanto entra el primero.

### 4.9 — ¿Esto funciona con blockchain?

**No usamos blockchain.** AuraHash es una arquitectura **offline-first** con criptografía estándar (Ed25519, AES-256-GCM). Blockchain requiere consenso distribuido y conexión, lo cual rompe el principio offline-first. Además, no aporta ventajas para este caso de uso.

### 4.10 — ¿Puedo ver todo el código?

**Sí.** AuraHash ID es MIT License. El repositorio es privado hoy, pero el código es auditable. Cualquier empresa que lo adopte puede revisarlo, modificarlo y desplegarlo.

### 4.11 — ¿Qué pasa si alguien clona mi pistola?

La pistola verifica firmas con la **llave pública** del organizador. Solo verifica, no firma. Una pistola clonada **no puede emitir boletos válidos**. Y el organizador puede revocar pistolas no autorizadas.

### 4.12 — ¿Y si el organizador quiere cancelar el evento?

El organizador emite una **nueva lista firmada** con todos los boletos cancelados. Las pistolas descargan esa lista y rechazan todos los boletos. Además, el organizador gestiona los reembolsos según su política.

### 4.13 — ¿Cómo se maneja el reembolso?

Configurable por el organizador. Ejemplos:
- **No reembolsable.**
- **Reembolso gratis hasta 48h antes.**
- **Reembolso hasta 15 min antes con cargo de $100 MXN.**
- **Reembolso siempre.**

La política se declara en el AuraHash del boleto. El comprador la acepta al comprar.

### 4.14 — ¿Qué pasa si la INE está vencida o es falsa?

El organizador decide qué nivel de verificación aplicar:
- **Básico:** hash de INE + nombre (no verifica contra RENAPO).
- **Avanzado:** integración con RENAPO (requiere convenio).
- **Con foto:** el staff compara la foto del boleto con la persona.

Cada nivel tiene costos y beneficios distintos.

---

## 5. Cómo lo implementaría un organizador (roadmap sugerido)

### Fase 1 — Piloto
- Elegir 1 evento pequeño.
- Integrar `generator.py` con el sistema de emisión existente.
- Emitir boletos con AuraHash en lugar de (o además de) los QR actuales.
- Staff con **app móvil** que verifica AuraHash (simple, sin pistola dedicada).
- Medir tiempos de ingreso, fraudes detectados, satisfacción del staff.

### Fase 2 — Expansión
- Integrar con `reader.py` en una app móvil oficial.
- Implementar lista firmada offline.
- Capacitar al staff.
- Medir auditoría post-evento.

### Fase 3 — Producción
- Integración completa con backend.
- Transferencias oficiales.
- Pistolas dedicadas.
- Aura Dinámica para wallet móvil.
- Métricas en tiempo real.

### Fase 4 — Escala
- Multi-venue, multi-evento.
- API pública para integraciones.
- SDK para terceros.

---

## 6. Diferenciación frente a otras soluciones

### 6.1 — Blockchain ticketing

**Problema:** requiere consenso distribuido y conexión. Rompe offline-first. Costos de gas (en algunas redes). No resuelve el problema de la fila.

**AuraHash:** offline-first. Sin blockchain. Criptografía estándar.

### 6.2 — Ticketmaster SafeTix

**Solución propietaria.** Requiere que el venue use su sistema completo. Cierra el ecosistema.

**AuraHash:** abierto (MIT). Cualquier organizador puede adoptarlo. Interoperable.

### 6.3 — Boletos QR estáticos

**Problema:** se copian, se comparten, se falsifican.

**AuraHash:** firmados + vinculados a INE. No se pueden copiar.

### 6.4 — Boletos nominativos con INE (sistemas actuales)

**Problema:** verifican INE en la entrada, pero dependen de red. Y el boleto en sí no está firmado criptográficamente.

**AuraHash:** verificación offline + firma Ed25519 + hash de INE.

---

## 7. Cierre del speech (30 segundos)

> "AuraHash ID no es un producto cerrado. Es un protocolo abierto. Cualquier organizador puede adoptarlo, adaptarlo, y desplegarlo sin depender de nosotros.
>
> Lo que ofrecemos es una arquitectura criptográfica probada, offline-first, que resuelve tres problemas concretos: fraude de boletos, reventa informal, y operación lenta en la fila.
>
> Si alguien aquí quiere explorar un piloto, con gusto conversamos. No vendemos software. Ofrecemos un camino.
>
> Gracias."

---

## 8. Preguntas para reflexionar antes de un piloto

Si un organizador se acerca interesado, estas son las preguntas que debería responder antes de comprometerse:

1. **¿Cuál es mi volumen de boletos por evento?** (Determina si la inversión vale la pena).
2. **¿Cuál es mi tasa actual de fraude?** (Si es cero, no hay urgencia).
3. **¿Mi venue tiene WiFi interna estable?** (Offline-first ayuda, pero WiFi interna facilita consolidación).
4. **¿Mi staff tiene capacidad técnica?** (La app debe ser muy simple).
5. **¿Mi sistema de emisión puede integrarse con AuraHash?** (Requiere desarrollo).
6. **¿Cuál es mi política de reembolso actual?** (AuraHash la modela, no la define).
7. **¿Estoy dispuesto a vincular boletos a INE?** (Decisión de negocio y legal).
8. **¿Qué pasa si el sistema falla en el evento?** (Plan de contingencia).

---

*Última actualización: 2026-10-15 — Pendiente #13 (flujo de eventos)*