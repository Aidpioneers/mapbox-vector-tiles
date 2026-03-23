#!/usr/bin/env python3

import requests
import pandas as pd
import json
import os
import re
from typing import Dict, Any

def normalize_column_name(col: str) -> str:
    """Convert sheet headers into stable machine-friendly names."""
    col = str(col).strip().lower()
    col = col.replace("&", "and")
    col = re.sub(r"[^\w\s]", "", col)   # remove ?, €, parentheses, etc.
    col = re.sub(r"\s+", "_", col)      # spaces -> underscores
    return col

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize columns and map important aliases to stable names."""
    df.columns = [normalize_column_name(col) for col in df.columns]

    rename_map = {}

    for col in df.columns:
        # Show column
        if col in ["show", "show_"]:
            rename_map[col] = "show"

        # Latitude / longitude
        elif col in ["lat", "latitude"]:
            rename_map[col] = "lat"
        elif col in ["lon", "lng", "long", "longitude"]:
            rename_map[col] = "lon"

        # Project/display name aliases
        elif col in ["project_name", "project", "name"]:
            rename_map[col] = "project_name"
        elif col in ["project_name_mapping", "project_mapping_name", "mapping_name"]:
            rename_map[col] = "project_name_mapping"

    df = df.rename(columns=rename_map)
    return df

def fetch_csv_to_geojson(url: str, raw_csv_name: str) -> Dict[str, Any]:
    """Fetch CSV from URL and convert to GeoJSON."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(raw_csv_name, "w", encoding="utf-8") as f:
            f.write(response.text)

        df = pd.read_csv(raw_csv_name)

        print(f"Original columns: {df.columns.tolist()}")
        print(f"Shape: {df.shape}")
        print(f"First few rows:\n{df.head()}")

        df = standardize_columns(df)

        print(f"Normalized columns: {df.columns.tolist()}")

        # Check coordinates
        if "lat" not in df.columns or "lon" not in df.columns:
            print(f"Could not find lat/lon columns in: {df.columns.tolist()}")
            return {"type": "FeatureCollection", "features": []}

        # Filter by show
        if "show" in df.columns:
            df["show"] = df["show"].astype(str).str.upper().str.strip()
            df = df[df["show"] == "TRUE"]

        # Convert coordinates
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

        # Drop invalid rows
        df = df.dropna(subset=["lat", "lon"])

        features = []
        for _, row in df.iterrows():
            properties = {}

            for col in df.columns:
                if col not in ["lat", "lon"]:
                    value = row[col]
                    properties[col] = "" if pd.isna(value) else str(value)

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["lon"]), float(row["lat"])]
                },
                "properties": properties
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        print(f"Error processing {raw_csv_name}: {e}")
        return {"type": "FeatureCollection", "features": []}

def fetch_and_convert_solar() -> Dict[str, Any]:
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJsNnPxAHbTwpovOYffeCdbZoVHBJzJI6vIWqvsV6Zj6S9PK0wpkUyoo27bXW8QxOaalujL_6VlfFP/pub?gid=1234705142&single=true&output=csv"
    return fetch_csv_to_geojson(url, "solar_data.csv")

def fetch_and_convert_medical() -> Dict[str, Any]:
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSwQfNVeLSL33IGytiDNV8DAduygRZ5xC0EBI1JLzrgjEFeKANCDTcQ9m9AcWgjtSOec5UcBUvOH_fW/pub?gid=1455555915&single=true&output=csv"
    return fetch_csv_to_geojson(url, "medical_data.csv")

def main():
    os.makedirs("data", exist_ok=True)

    print("Fetching solar data...")
    solar_geojson = fetch_and_convert_solar()

    print("Fetching medical data...")
    medical_geojson = fetch_and_convert_medical()

    with open("data/solar.geojson", "w", encoding="utf-8") as f:
        json.dump(solar_geojson, f, indent=2, ensure_ascii=False)

    with open("data/medical.geojson", "w", encoding="utf-8") as f:
        json.dump(medical_geojson, f, indent=2, ensure_ascii=False)

    combined_features = solar_geojson["features"] + medical_geojson["features"]
    combined_geojson = {
        "type": "FeatureCollection",
        "features": combined_features
    }

    with open("data/combined.geojson", "w", encoding="utf-8") as f:
        json.dump(combined_geojson, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(solar_geojson['features'])} solar features")
    print(f"Generated {len(medical_geojson['features'])} medical features")
    print(f"Combined {len(combined_features)} total features")

if __name__ == "__main__":
    main()
