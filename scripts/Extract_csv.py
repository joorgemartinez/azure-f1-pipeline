#!/usr/bin/env python3
import os
import io
import sys
import argparse
import urllib.parse
import requests
import certifi
import pandas as pd

DEFAULT_URLS = [
    "https://api.openf1.org/v1/sessions?year=2023&csv=true",
    "https://api.openf1.org/v1/session_result?session_key=9094&csv=true",
    "https://api.openf1.org/v1/drivers?session_key=9094&csv=true"
]

def get_clean_name(url):
    parsed = urllib.parse.urlparse(url)
    endpoint = os.path.basename(parsed.path.rstrip("/"))
    query = urllib.parse.parse_qs(parsed.query)

    if "session_key" in query:
        return f"{endpoint}_{query['session_key'][0]}"
    if "year" in query:
        return f"{endpoint}_{query['year'][0]}"
    if "meeting_key" in query:
        return f"{endpoint}_{query['meeting_key'][0]}"

    for k, v in query.items():
        if k.lower() != "csv":
            return f"{endpoint}_{k}-{v[0]}"
    return endpoint

def download_csv(url):
    r = requests.get(url, timeout=30, verify=certifi.where())
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", action="append", help="URL (puedes repetir varias veces)")
    parser.add_argument("-o", "--out", default="data", help="Directorio de salida relativo al proyecto (por defecto: data)")
    args = parser.parse_args()

    # --- Detectar la raíz del proyecto ---
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root_dir, args.out)
    os.makedirs(out_dir, exist_ok=True)

    urls = args.url or DEFAULT_URLS

    for url in urls:
        try:
            print(f"Descargando {url} ...")
            df = download_csv(url)
            name = get_clean_name(url)
            path = os.path.join(out_dir, f"{name}.csv")
            df.to_csv(path, index=False)
            print(f"Guardado en {path} ({len(df)} filas)")
        except Exception as e:
            print(f"Error descargando {url}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
