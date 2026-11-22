// server.js - API + panel web del Medidor UV para colegios de Peñalolén
// ---------------------------------------------------------------------
// ESP32 --(HTTPS POST cada 10 s)--> este servidor (Railway) --> PostgreSQL (Aiven)
// La página web (carpeta public/) consulta esta misma API y muestra:
//   estado actual, alerta, recomendación para el colegio, estadísticas del día,
//   gráfico histórico y tabla de lecturas.
//
// Basado en el ejemplo de la "Guía TEI: ESP32 + Aiven + Railway" (TEI201, 2026).
// Cambios respecto de la guía: tabla adaptada al índice UV, cálculo del nivel OMS
// en el servidor, rutas /api/ultima, /api/historial, /api/resumen y /api/exportar.csv.

require("dotenv").config();
const express = require("express");
const path = require("path");
const { Pool } = require("pg");

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const ZONA = "America/Santiago";   // hora de Chile para "hoy"
const ENTRE_LECTURAS_MAX_S = 60;   // si pasan más de 60 s sin datos, ese tramo no se cuenta

// ---------- Conexión a la base de datos (Aiven exige SSL) ----------
const pool = new Pool({
  connectionString: (process.env.DATABASE_URL || "").split("?")[0],
  ssl: process.env.DB_CA_CERT
    ? { ca: process.env.DB_CA_CERT.replace(/\\n/g, "\n") }
    : process.env.DB_SIN_SSL === "1" ? false : { rejectUnauthorized: false },
  max: 5,
});

async function crearTabla() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS lecturas_uv (
      id          SERIAL PRIMARY KEY,
      dispositivo VARCHAR(50)  NOT NULL,
      indice_uv   REAL         NOT NULL,
      milivoltios INTEGER      NOT NULL,
      nivel       VARCHAR(12)  NOT NULL,
      creado_en   TIMESTAMPTZ  DEFAULT NOW()
    )
  `);
  await pool.query("CREATE INDEX IF NOT EXISTS lecturas_uv_fecha ON lecturas_uv (creado_en)");
  console.log("Tabla 'lecturas_uv' lista");
}

// ---------- Escala UV de la OMS (igual que en el ESP32) ----------
// 0-2 BAJO, 3-5 MODERADO, 6-7 ALTO, 8-10 MUY ALTO, 11+ EXTREMO (índice redondeado)
function nivelOMS(uv) {
  const i = Math.round(uv);
  if (i <= 2) return "BAJO";
  if (i <= 5) return "MODERADO";
  if (i <= 7) return "ALTO";
  if (i <= 10) return "MUY ALTO";
  return "EXTREMO";
}

// Orden numérico del nivel, para comparar en SQL (0 = BAJO ... 4 = EXTREMO)
const SQL_RANGO_NIVEL = `CASE nivel WHEN 'BAJO' THEN 0 WHEN 'MODERADO' THEN 1
  WHEN 'ALTO' THEN 2 WHEN 'MUY ALTO' THEN 3 ELSE 4 END`;

// Inicio del día de hoy en hora de Chile
const SQL_INICIO_HOY = `(date_trunc('day', NOW() AT TIME ZONE '${ZONA}') AT TIME ZONE '${ZONA}')`;

// ---------- Seguridad mínima: clave compartida con el ESP32 ----------
function revisarClave(req, res, next) {
  if (!process.env.API_KEY || req.get("x-api-key") !== process.env.API_KEY) {
    return res.status(401).json({ error: "API key invalida" });
  }
  next();
}

// ---------- Rutas ----------
app.get("/api/salud", async (req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ ok: true, db: "conectada" });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

// El ESP32 manda: {"dispositivo":"uv-colegio-1","indice_uv":4.3,"milivoltios":520,"nivel":"MODERADO"}
// "nivel" es opcional: si viene, es el mismo que muestra el semáforo (ya confirmado con
// 4 lecturas seguidas, así no parpadea en los límites). Si no viene, se calcula aquí.
const NIVELES_VALIDOS = ["BAJO", "MODERADO", "ALTO", "MUY ALTO", "EXTREMO"];
app.post("/api/lecturas", revisarClave, async (req, res) => {
  const { dispositivo, indice_uv, milivoltios } = req.body;
  if (!dispositivo || typeof indice_uv !== "number" || typeof milivoltios !== "number") {
    return res.status(400).json({ error: "Faltan campos o no son numeros" });
  }
  // Rango físico posible del sensor: descarta lecturas absurdas (ruido, cable suelto)
  if (indice_uv < 0 || indice_uv > 20 || milivoltios < 0 || milivoltios > 3300) {
    return res.status(400).json({ error: "Lectura fuera de rango" });
  }
  try {
    const nivel = NIVELES_VALIDOS.includes(req.body.nivel) ? req.body.nivel : nivelOMS(indice_uv);
    const r = await pool.query(
      "INSERT INTO lecturas_uv (dispositivo, indice_uv, milivoltios, nivel) VALUES ($1, $2, $3, $4) RETURNING id",
      [String(dispositivo).slice(0, 50), indice_uv, Math.round(milivoltios), nivel]
    );
    res.status(201).json({ ok: true, id: r.rows[0].id, nivel });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al guardar" });
  }
});

// Últimas lecturas crudas (para la tabla)
app.get("/api/lecturas", async (req, res) => {
  const limite = Math.min(parseInt(req.query.limite) || 50, 500);
  try {
    const r = await pool.query("SELECT * FROM lecturas_uv ORDER BY id DESC LIMIT $1", [limite]);
    res.json(r.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al leer" });
  }
});

// Lectura más reciente + segundos desde que llegó (para saber si el equipo está en línea)
app.get("/api/ultima", async (req, res) => {
  try {
    const r = await pool.query(`
      SELECT *, EXTRACT(EPOCH FROM (NOW() - creado_en))::int AS hace_s
      FROM lecturas_uv ORDER BY id DESC LIMIT 1`);
    res.json(r.rows[0] || null);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al leer" });
  }
});

// Historial agrupado para el gráfico: promedio y máximo por tramo de tiempo
app.get("/api/historial", async (req, res) => {
  const horas = Math.min(Math.max(parseFloat(req.query.horas) || 1, 0.25), 24 * 7);
  // Tamaño del tramo según el rango: así el gráfico nunca tiene más de ~300 puntos
  const tramo_s = horas <= 1 ? 10 : horas <= 6 ? 60 : horas <= 24 ? 300 : 1800;
  try {
    const r = await pool.query(`
      SELECT to_timestamp(floor(EXTRACT(EPOCH FROM creado_en) / $2) * $2) AS t,
             ROUND(AVG(indice_uv)::numeric, 2)::float AS promedio,
             ROUND(MAX(indice_uv)::numeric, 2)::float AS maximo,
             COUNT(*)::int AS n
      FROM lecturas_uv
      WHERE creado_en >= NOW() - make_interval(secs => $1 * 3600)
      GROUP BY 1 ORDER BY 1`, [horas, tramo_s]);
    res.json({ horas, tramo_s, puntos: r.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al leer" });
  }
});

// Información útil del día: máximo, promedio, minutos en cada nivel y alertas
app.get("/api/resumen", async (req, res) => {
  try {
    const general = await pool.query(`
      SELECT COUNT(*)::int AS lecturas,
             ROUND(AVG(indice_uv)::numeric, 1)::float AS promedio,
             MIN(creado_en) AS primera, MAX(creado_en) AS ultima
      FROM lecturas_uv WHERE creado_en >= ${SQL_INICIO_HOY}`);

    const maximo = await pool.query(`
      SELECT indice_uv, nivel, creado_en FROM lecturas_uv
      WHERE creado_en >= ${SQL_INICIO_HOY}
      ORDER BY indice_uv DESC, creado_en ASC LIMIT 1`);

    // Minutos en cada nivel: tiempo entre una lectura y la siguiente (máx. 60 s por tramo)
    const minutos = await pool.query(`
      WITH hoy AS (
        SELECT nivel, creado_en,
               LEAD(creado_en) OVER (ORDER BY creado_en) AS siguiente
        FROM lecturas_uv WHERE creado_en >= ${SQL_INICIO_HOY}
      )
      SELECT nivel,
             ROUND((SUM(LEAST(EXTRACT(EPOCH FROM (COALESCE(siguiente, NOW()) - creado_en)), $1)) / 60)::numeric, 1)::float AS minutos
      FROM hoy GROUP BY nivel`, [ENTRE_LECTURAS_MAX_S]);

    // Alertas: veces que el nivel SUBIÓ a ALTO o más (antes estaba bajo ALTO)
    const alertas = await pool.query(`
      WITH hoy AS (
        SELECT creado_en, ${SQL_RANGO_NIVEL} AS rango,
               LAG(${SQL_RANGO_NIVEL}) OVER (ORDER BY creado_en) AS rango_previo
        FROM lecturas_uv WHERE creado_en >= ${SQL_INICIO_HOY}
      )
      SELECT COUNT(*)::int AS alertas, MIN(creado_en) AS primera_alerta
      FROM hoy WHERE rango >= 2 AND (rango_previo IS NULL OR rango_previo < 2)`);

    // Máximo de cada uno de los últimos 7 días (para comparar días)
    const dias = await pool.query(`
      SELECT to_char(creado_en AT TIME ZONE '${ZONA}', 'YYYY-MM-DD') AS dia,
             ROUND(MAX(indice_uv)::numeric, 1)::float AS maximo,
             COUNT(*)::int AS lecturas
      FROM lecturas_uv WHERE creado_en >= ${SQL_INICIO_HOY} - INTERVAL '6 days'
      GROUP BY 1 ORDER BY 1`);

    const porNivel = { "BAJO": 0, "MODERADO": 0, "ALTO": 0, "MUY ALTO": 0, "EXTREMO": 0 };
    minutos.rows.forEach(f => { porNivel[f.nivel] = f.minutos; });
    const minutosConProteccion =
      porNivel["MODERADO"] + porNivel["ALTO"] + porNivel["MUY ALTO"] + porNivel["EXTREMO"];

    res.json({
      ...general.rows[0],
      maximo: maximo.rows[0] || null,
      minutos_por_nivel: porNivel,
      minutos_con_proteccion: Math.round(minutosConProteccion * 10) / 10,
      alertas: alertas.rows[0].alertas,
      primera_alerta: alertas.rows[0].primera_alerta,
      ultimos_dias: dias.rows,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al calcular el resumen" });
  }
});

// Descarga de datos en CSV (para el informe de testing)
app.get("/api/exportar.csv", async (req, res) => {
  const horas = Math.min(Math.max(parseFloat(req.query.horas) || 24, 0.25), 24 * 31);
  try {
    const r = await pool.query(`
      SELECT id, dispositivo, indice_uv, milivoltios, nivel,
             to_char(creado_en AT TIME ZONE '${ZONA}', 'YYYY-MM-DD HH24:MI:SS') AS fecha_chile
      FROM lecturas_uv WHERE creado_en >= NOW() - make_interval(secs => $1 * 3600)
      ORDER BY id`, [horas]);
    const filas = ["id,dispositivo,indice_uv,milivoltios,nivel,fecha_chile"];
    r.rows.forEach(f => filas.push(
      [f.id, f.dispositivo, f.indice_uv, f.milivoltios, f.nivel, f.fecha_chile].join(",")));
    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition", "attachment; filename=lecturas_uv.csv");
    res.send(filas.join("\n"));
  } catch (err) {
    console.error(err);
    res.status(500).send("Error al exportar");
  }
});

// ---------- Arranque ----------
const PORT = process.env.PORT || 3000; // Railway define PORT solo
app.listen(PORT, async () => {
  console.log(`Servidor escuchando en el puerto ${PORT}`);
  try {
    await crearTabla();
  } catch (err) {
    console.error("No se pudo conectar a la base de datos:", err.message);
  }
});
