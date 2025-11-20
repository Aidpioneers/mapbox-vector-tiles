#!/usr/bin/env python3

import requests
import pandas as pd
import json
import os

def fetch_and_convert_marathons():
    """Fetch marathons data from Google Sheets and convert to GeoJSON"""
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDhMx8shcqFiqMKjLnrC0NNhV3b_kNCyn7FfpT0IYd8gPJf0VnKtgkGSmtJRWzbTaLR1LtSeMnmwny/pub?gid=1011192317&single=true&output=csv"
    
    response = requests.get(url)
    response.raise_for_status()
    
    # Read CSV
    df = pd.read_csv(url)
    
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    
    # Find geolocation column
    geoloc_col = None
    for col in df.columns:
        if 'geolocation' in col.lower() or 'location' in col.lower():
            geoloc_col = col
            break
    
    if not geoloc_col:
        print("ERROR: No geolocation column found!")
        return {"type": "FeatureCollection", "features": []}
    
    features = []
    for idx, row in df.iterrows():
        try:
            geoloc = str(row[geoloc_col]).strip()
            if pd.isna(row[geoloc_col]) or geoloc == '' or geoloc == 'nan':
                continue
            
            parts = geoloc.split(',')
            if len(parts) != 2:
                continue
            
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue
            
            properties = {}
            for col in df.columns:
                if col != geoloc_col:
                    value = row[col]
                    properties[col] = str(value) if pd.notna(value) else ""
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": properties
            }
            
            features.append(feature)
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    print(f"Created GeoJSON with {len(features)} features")
    return geojson

def main():
    geojson_data = fetch_and_convert_marathons()
    
    output_path = 'data/marathons.geojson'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
