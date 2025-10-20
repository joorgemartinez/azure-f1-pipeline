#!/usr/bin/env python3
# Extract_csv_pretty.py
import os, io, sys, argparse, urllib.parse
import requests, certifi
import pandas as pd

DEFAULT_URLS = [
    "https://api.openf1.org/v1/sessions?year=2023&csv=true",
    "https://api.openf1.org/v1/session_result?session_key=9094&csv=true",
    "https://api.openf1.org/v1/drivers?session_key=9094&csv=true",
]

def pretty_name_from_url(url: str) -> str:
    """
    Genera un nombre de archivo 'bonito' a partir del endpoint y los parámetros:
    - sessions?year=2023   -> sessions_2023
    - session_result?session_key=9094 -> session_result_9094
    - drivers?session_key=9094 -> drivers_9094
    Fallback: endpoint + params concatenados.
    """
    parsed = urllib.parse.urlparse(url)
    endpoint = os.path.basename(parsed.path.rstrip("/"))  # sessions, drivers, session_result, etc.
    q = urllib.parse.parse_qs(parsed.query)  # dict: { 'year': ['2023'], 'session_key': ['9094'], 'csv': ['true'] }

    # prioridad de parámetros “clave”
    if "session_key" in q and q["session_key"]:
        return f"{endpoint}_{q['session_key'][0]}"
    if "year" in q and q["year"]:
        return f"{endpoint}_{q['year'][0]}"
    if "meeting_key" in q and q["meeting_key"]:
        return f"{endpoint}_{q['meeting_key'][0]}"

    # si no hay ninguno de los anteriores, arma algo legible sin csv=true
    filtered = {k: v for k, v in q.items() if k.lower() != "csv"}
    if filtered:
        flat = "_".join(f"{k}-{v[0]}" for k, v in filtered.items())
        return f"{endpoint}_{flat}"

    return endpoint  # último recurso

def fetch_csv(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=30, verify=certifi.where())
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

def main():
    p = argparse.ArgumentParser(description="Descarga CSVs de OpenF1 con nombres de archivo limpios.")
    p.add_argument("-o", "--out-dir", default="data", help="Directorio de salida (por defecto: data)")
    p.add_argument("-u", "--url", action="append",
                   help="URL(s) CSV a descargar (repetir -u). Si no se pasa, usa un set por defecto.")
    args = p.parse_args()

    urls = args.url or DEFAULT_URLS
    os.makedirs(args.out_dir, exist_ok=True)

    for url in urls:
        try:
            print(f"🔹 Descargando: {url}")
            df = fetch_csv(url)
            base = pretty_name_from_url(url)
            out_path = os.path.join(args.out_dir, f"{base}.csv")
            df.to_csv(out_path, index=False)
            print(f"✅ Guardado: {out_path} ({len(df)} filas)")
        except Exception as e:
            print(f"❌ Error con {url}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
