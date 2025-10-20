#!/usr/bin/env python3
# raw -> silver (FP3 Monaco 2023 - session_key=9089)
import os
import shutil
from pyspark.sql import SparkSession, functions as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "silver")
OUT_FILE = os.path.join(OUT_DIR, "f1_results_silver_fp3_2023.csv")

def main():
    spark = (SparkSession.builder
             .appName("f1-raw-to-silver-fp3-9089")
             .getOrCreate())

    # --- RAW ---
    sessions = spark.read.option("header", True).csv(os.path.join(DATA, "sessions_2023.csv"))
    results  = spark.read.option("header", True).csv(os.path.join(DATA, "session_result_9089.csv"))
    drivers  = spark.read.option("header", True).csv(os.path.join(DATA, "drivers_9089.csv"))

    # --- Limpieza ---
    sessions = (sessions
        .withColumn("year", F.col("year").cast("int"))
        .withColumn("session_key", F.col("session_key").cast("int"))
        .withColumn("meeting_key", F.col("meeting_key").cast("int"))
        .withColumn("date_start", F.to_timestamp("date_start"))
        .withColumn("date_end", F.to_timestamp("date_end"))
    )

    results = (results
        .withColumn("session_key", F.col("session_key").cast("int"))
        .withColumn("meeting_key", F.col("meeting_key").cast("int"))
        .withColumn("driver_number", F.col("driver_number").cast("int"))
        .withColumn("position", F.col("position").cast("int"))
        .withColumn("number_of_laps", F.col("number_of_laps").cast("int"))
        .withColumn("gap_to_leader", F.col("gap_to_leader").cast("double"))
        .withColumn("duration_sec", F.col("duration").cast("double"))
        .withColumn("dnf", F.col("dnf").cast("boolean"))
        .withColumn("dns", F.col("dns").cast("boolean"))
        .withColumn("dsq", F.col("dsq").cast("boolean"))
        .withColumn(
            "status",
            F.when(F.col("dsq") == True, "DSQ")
             .when(F.col("dnf") == True, "DNF")
             .when(F.col("dns") == True, "DNS")
             .otherwise(None)
        )
        .withColumn("laps_completed", F.col("number_of_laps"))
        .withColumn("points", F.lit(0.0).cast("double"))
    )

    drivers = (drivers
        .withColumn("session_key", F.col("session_key").cast("int"))
        .withColumn("driver_number", F.col("driver_number").cast("int"))
    )

    # eliminar duplicados de meeting_key
    for df in [results, drivers]:
        if "meeting_key" in df.columns:
            df = df.drop("meeting_key")

    joined = (results.alias("r")
        .join(drivers.alias("d"), ["session_key", "driver_number"], "left")
        .join(sessions.alias("s"), "session_key", "left")
    )

    silver = (joined.select(
        F.col("r.session_key"),
        F.col("s.meeting_key"),
        F.col("s.year"),
        F.col("s.session_type"),
        F.col("s.session_name"),
        F.col("s.circuit_short_name"),
        F.col("s.country_name"),
        F.col("s.date_start"),
        F.col("r.driver_number"),
        F.col("d.full_name"),
        F.col("d.team_name"),
        F.col("r.position"),
        F.col("r.points"),
        F.col("r.laps_completed"),
        F.col("r.duration_sec"),
        F.col("r.gap_to_leader"),
        F.col("r.status")
    ).dropDuplicates(["session_key", "driver_number"])
    )

    # --- Guardado CSV limpio ---
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp_dir = OUT_FILE + "_tmp"

    (silver
        .coalesce(1)
        .write
        .option("header", True)
        .mode("overwrite")
        .csv(tmp_dir))

    # buscar el archivo CSV dentro de la carpeta temporal
    csv_path = None
    for file in os.listdir(tmp_dir):
        if file.endswith(".csv"):
            csv_path = os.path.join(tmp_dir, file)
            shutil.move(csv_path, OUT_FILE)
            break

    # eliminar carpeta temporal completa
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"CSV generado correctamente en: {OUT_FILE}")
    spark.stop()

if __name__ == "__main__":
    main()
