/**
 * AuraHash ID - Barrido de opacidades 7x6 en la consola del navegador
 * ===================================================================
 *
 * Requisitos:
 *   - Servidor corriendo en pwa/ (http://localhost:8000)
 *   - 42 PNGs en pwa/batch/ (b7_<id_escenario>_op<NN>.png)
 *   - PWA abierta en http://localhost:8000/
 *
 * Uso:
 *   1. Abrir DevTools (F12) -> pestana Console
 *   2. Pegar TODO este archivo
 *   3. Enter
 *   4. Al terminar, se descarga barrido_opacidades_<timestamp>.json
 *
 * Estrategia dual (identica a index.html v2.0.1):
 *   Intento 1: imagen completa
 *   Intento 2: crop 70% central
 */

(async () => {
  "use strict";

  // =====================================================================
  // CONFIGURACION
  // =====================================================================

  const ESCENARIOS = [
    "salud_emergencia_02",
    "personal_ciclista_01",
    "evento_boleto_01",
    "seguro_auto_01",
    "contacto_nino_01",
    "legal_contrato_02",
    "militar_inteligencia_01",
  ];

  const OPACIDADES_PCT = [0, 1, 2, 3, 4, 5];

  const GENERATOR_VERSION = "v3.0.1";
  const CROP_FACTOR = 0.70;

  // =====================================================================
  // HINTS (identicos a index.html)
  // =====================================================================

  const hints = new Map();
  hints.set(ZXing.DecodeHintType.POSSIBLE_FORMATS, [
    ZXing.BarcodeFormat.DATA_MATRIX,
    ZXing.BarcodeFormat.QR_CODE,
  ]);
  hints.set(ZXing.DecodeHintType.TRY_HARDER, true);

  // =====================================================================
  // UTILIDADES
  // =====================================================================

  function cargarImagen(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("No se pudo cargar: " + src));
      img.src = src + "?t=" + Date.now();
    });
  }

  function recortarCentro(img, factor) {
    const w = img.naturalWidth;
    const h = img.naturalHeight;
    const cropSize = Math.floor(Math.min(w, h) * factor);
    const cropX = Math.floor((w - cropSize) / 2);
    const cropY = Math.floor((h - cropSize) / 2);

    const canvas = document.createElement("canvas");
    canvas.width = cropSize;
    canvas.height = cropSize;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, cropX, cropY, cropSize, cropSize, 0, 0, cropSize, cropSize);
    return canvas;
  }

  async function intentarDecodificar(img) {
    // Intento 1: imagen completa
    try {
      const reader = new ZXing.BrowserMultiFormatReader(hints);
      const res = await reader.decodeFromImageElement(img);
      return { ok: true, modo: "completa", texto: res.getText() };
    } catch (e1) {
      // Intento 2: crop 70%
      try {
        const canvas = recortarCentro(img, CROP_FACTOR);
        const reader2 = new ZXing.BrowserMultiFormatReader(hints);
        const res2 = await reader2.decodeFromCanvas(canvas);
        return { ok: true, modo: "crop70", texto: res2.getText() };
      } catch (e2) {
        return { ok: false, modo: null, texto: null };
      }
    }
  }

  // =====================================================================
  // BARRIDO
  // =====================================================================

  console.log("=".repeat(60));
  console.log("  AuraHash ID - Barrido de opacidades 7x6");
  console.log("  Escenarios: " + ESCENARIOS.length);
  console.log("  Opacidades: " + OPACIDADES_PCT.join(", ") + "%");
  console.log("  Total pruebas: " + (ESCENARIOS.length * OPACIDADES_PCT.length));
  console.log("=".repeat(60));
  console.log("");

  const resultados = {}; // resultados[id][pct] = { ok, modo, chars }
  for (const id of ESCENARIOS) {
    resultados[id] = {};
  }

  let contador = 0;
  const total = ESCENARIOS.length * OPACIDADES_PCT.length;

  for (const id of ESCENARIOS) {
    for (const pct of OPACIDADES_PCT) {
      contador++;
      const opNN = String(pct).padStart(2, "0");
      const src = "batch/b7_" + id + "_op" + opNN + ".png";

      try {
        const img = await cargarImagen(src);
        const r = await intentarDecodificar(img);

        if (r.ok) {
          console.log(
            "\u2705 [" + contador + "/" + total + "] " + id + " @ " + pct + "%: OK (" +
            r.modo + ", " + r.texto.length + " chars)"
          );
          resultados[id][pct] = { ok: true, modo: r.modo, chars: r.texto.length };
        } else {
          console.log(
            "\u274C [" + contador + "/" + total + "] " + id + " @ " + pct + "%: FALLA"
          );
          resultados[id][pct] = { ok: false, modo: null, chars: 0 };
        }
      } catch (e) {
        console.log(
          "\u26A0\uFE0F [" + contador + "/" + total + "] " + id + " @ " + pct + "%: ERROR " + e.message
        );
        resultados[id][pct] = { ok: false, modo: null, chars: 0, error: e.message };
      }
    }
  }

  // =====================================================================
  // RESUMEN POR ESCENARIO
  // =====================================================================

  console.log("");
  console.log("=".repeat(60));
  console.log("  RESUMEN POR ESCENARIO");
  console.log("=".repeat(60));

  for (const id of ESCENARIOS) {
    const okOps = OPACIDADES_PCT.filter((p) => resultados[id][p].ok);
    const marca = okOps.length === OPACIDADES_PCT.length ? "\u2705" : (okOps.length === 0 ? "\u274C" : "\u26A0\uFE0F");
    console.log(
      marca + " " + id.padEnd(28) + " OK en: [" + okOps.join(", ") + "]"
    );
  }

  // =====================================================================
  // RESUMEN POR OPACIDAD
  // =====================================================================

  console.log("");
  console.log("=".repeat(60));
  console.log("  RESUMEN POR OPACIDAD");
  console.log("=".repeat(60));

  const tasaPorOpacidad = {};
  for (const pct of OPACIDADES_PCT) {
    const okIds = ESCENARIOS.filter((id) => resultados[id][pct].ok);
    const tasa = okIds.length / ESCENARIOS.length;
    tasaPorOpacidad[pct] = {
      ok: okIds.length,
      total: ESCENARIOS.length,
      tasa: tasa,
      ids_ok: okIds,
    };
    const barra = "#".repeat(okIds.length) + ".".repeat(ESCENARIOS.length - okIds.length);
    console.log(
      "  " + pct + "%: " + barra + "  " + okIds.length + "/" + ESCENARIOS.length +
      "  (" + Math.round(tasa * 100) + "%)"
    );
  }

  // =====================================================================
  // OPACIDADES QUE FUNCIONAN PARA LOS 7
  // =====================================================================

  const opacidadesPerfectas = OPACIDADES_PCT.filter(
    (pct) => ESCENARIOS.every((id) => resultados[id][pct].ok)
  );

  console.log("");
  console.log("=".repeat(60));
  console.log("  OPACIDADES QUE FUNCIONAN PARA LOS 7");
  console.log("=".repeat(60));

  let opacidadRecomendada = null;
  if (opacidadesPerfectas.length > 0) {
    opacidadRecomendada = Math.max(...opacidadesPerfectas);
    console.log("  \u2705 [" + opacidadesPerfectas.join(", ") + "]");
    console.log("  \u2192 Opacidad recomendada (la mas alta): " + opacidadRecomendada + "%");
  } else {
    // Ninguna funciona para los 7: elegir la de mayor tasa
    let mejor = OPACIDADES_PCT[0];
    let mejorTasa = tasaPorOpacidad[mejor].ok;
    for (const pct of OPACIDADES_PCT) {
      if (tasaPorOpacidad[pct].ok > mejorTasa) {
        mejor = pct;
        mejorTasa = tasaPorOpacidad[pct].ok;
      } else if (tasaPorOpacidad[pct].ok === mejorTasa && pct > mejor) {
        mejor = pct;
      }
    }
    opacidadRecomendada = mejor;
    console.log("  \u26A0\uFE0F Ninguna opacidad funciona para los 7.");
    console.log("  \u2192 Mejor opacidad parcial: " + mejor + "% (" + mejorTasa + "/7)");
  }

  // =====================================================================
  // JSON DE RESULTADOS
  // =====================================================================

  const ahora = new Date();
  const timestamp = ahora.toISOString().replace(/[:.]/g, "-").slice(0, 19);

  const json = {
    meta: {
      proyecto: "AuraHash ID",
      generador_version: GENERATOR_VERSION,
      fecha_iso: ahora.toISOString(),
      fecha_local: ahora.toLocaleString("es-MX"),
      navegador: navigator.userAgent,
      crop_factor: CROP_FACTOR,
      estrategia: "dual (imagen completa + crop 70%)",
      total_pruebas: total,
    },
    escenarios: ESCENARIOS,
    opacidades_probadas_pct: OPACIDADES_PCT,
    resultados: resultados,
    resumen_por_escenario: ESCENARIOS.reduce((acc, id) => {
      acc[id] = OPACIDADES_PCT.filter((p) => resultados[id][p].ok);
      return acc;
    }, {}),
    resumen_por_opacidad: Object.fromEntries(
      OPACIDADES_PCT.map((pct) => [
        pct,
        {
          ok: tasaPorOpacidad[pct].ok,
          total: tasaPorOpacidad[pct].total,
          tasa: Number(tasaPorOpacidad[pct].tasa.toFixed(3)),
          ids_ok: tasaPorOpacidad[pct].ids_ok,
        },
      ])
    ),
    opacidades_que_funcionan_para_los_7: opacidadesPerfectas,
    opacidad_recomendada_pct: opacidadRecomendada,
  };

  const blob = new Blob([JSON.stringify(json, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "barrido_opacidades_" + timestamp + ".json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  console.log("");
  console.log("=".repeat(60));
  console.log("  JSON DESCARGADO: barrido_opacidades_" + timestamp + ".json");
  console.log("=".repeat(60));
  console.log("");
  console.log("  Comparte ese archivo con la IA para actualizar el mini-contexto.");
  console.log("");
})();