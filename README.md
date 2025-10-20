# 🏎️ Azure F1 Pipeline – FP3 Monaco 

Pipeline de ingeniería de datos inspirado en arquitectura **Azure Data Lakehouse**, utilizando datos abiertos de **OpenF1**.

El proyecto replica un flujo **RAW → SILVER**, empleando **PySpark** para limpiar, transformar y estandarizar la información de la **FP3 del GP de Mónaco 2023**.  
El siguiente paso (en desarrollo) será la capa **GOLD**, desplegada en **Azure Databricks**.

---

## 📂 Estructura del proyecto

```bash
azure-f1-pipeline/
│
├── data/                             # Datos RAW extraídos de la API de OpenF1
│   ├── sessions_2023.csv              # Información de todas las sesiones de 2023
│   ├── drivers_9089.csv               # Datos de pilotos (FP3 Mónaco 2023)
│   └── session_result_9089.csv        # Resultados FP3 Mónaco 2023
│
├── scripts/                          # Lógica principal del pipeline
│   ├── Extract_csv.py          # Script de extracción desde OpenF1 API
│   └── silver_job.py                  # Transformaciones PySpark (RAW → SILVER)
│
├── silver/                           # Capa Silver (datos limpios listos para análisis)
│   └── f1_results_silver_fp3_2023.csv # Dataset consolidado y normalizado
│
├── gold/                             # (Próximamente) Capa Gold - KPIs y métricas agregadas
│
└── README.md                         # Documentación principal del proyecto
```

---

## ⚙️ Flujo de datos

**1️⃣ Extracción (RAW):**  
Mediante `Extract_csv_pretty.py`, se consultan los endpoints CSV públicos de OpenF1 y se guardan localmente en la carpeta `data/`.

**2️⃣ Transformación (SILVER):**  
El job `silver_job.py` utiliza **PySpark** para:
- Cargar los datasets `sessions`, `drivers` y `session_result`.  
- Convertir tipos de datos (`int`, `double`, `timestamp`, `boolean`).  
- Estandarizar métricas (`duration_sec`, `laps_completed`).  
- Unir las tablas y derivar el campo `status` (`DSQ`, `DNF`, `DNS`).  
- Generar un CSV final limpio y unificado en `silver/`.

**3️⃣ (Próximamente) Capa GOLD:**  
Resumen analítico para Power BI / Synapse:  
- Medias de tiempo por equipo.  
- Gaps promedio respecto al líder.  
- Ranking de pilotos por sesión.

---

## 🧩 Stack tecnológico

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| Ingesta de datos | **OpenF1 API (CSV endpoints)** | Datos públicos de sesiones F1 |
| Procesamiento | **PySpark (local / Databricks-ready)** | Limpieza, joins y transformaciones |
| Almacenamiento | **Data Lake (local → Azure Data Lake)** | Estructura RAW / SILVER / GOLD |
| Orquestación *(futuro)* | **Azure Data Factory / Airflow** | Automatización de jobs |
| Análisis *(futuro)* | **Power BI / Azure Synapse** | Visualización de métricas F1 |

---

## 🚀 Ejecución local

### 1. Crear entorno y dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install pyspark pandas requests certifi
```

###  2. Descargar los CSVs desde OpenF1

El script `Extract_csv.py` permite descargar los datasets directamente desde los endpoints públicos de **OpenF1**.

```bash
python3 scripts/Extract_csv.py
```
Esto genera los archivos CSV en la carpeta `data/`:

```bash
data/
 ├── sessions_2023.csv
 ├── drivers_9089.csv
 └── session_result_9089.csv
```

### 3. Ejecutar el job de limpieza (RAW → SILVER)
El script `silver_job.py` utiliza PySpark para limpiar, transformar y unir los datasets.

```bash
python3 scripts/silver_job.py
```

El resultado es un dataset limpio y consolidado listo para análisis:

```bash
silver/
 └── f1_results_silver_fp3_2023.csv
```
---

## 📊 Próximos pasos
- Añadir capa GOLD con agregaciones y KPIs
- Migrar el pipeline a Azure Databricks
- Publicar dashboard en Power BI Service
- Añadir orquestación con Azure Data Factory o Airflow
- Implementar almacenamiento en Azure Data Lake (ADLS Gen2)