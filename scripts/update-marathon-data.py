#!/usr/bin/env python3

import requests
import pandas as pd
import json
import os
from typing import Dict, Any

def fetch_and_convert_to_geojson() -> Dict[str, Any]:
    """Fetch marathon data from Google Sheets and convert to GeoJSON"""
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDhMx8shcqFiqMKjLnrC0NNhV3b_kNCyn7FfpT0IYd8gPJf0VnKtgkGSmtJRWzbTaLR1LtSeMnmwny/pub?gid=730702317&single=true&output=csv"
    
    try:
        print("Fetching data from Google Sheets...")
        response = requests.get(url)
        response.raise_for_status()
        
        # Save raw CSV for debugging
        with open('temp_data.csv', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Read CSV with pandas
        df = pd.read_csv('temp_data.csv')
        
        print(f"Data columns: {df.columns.tolist()}")
        print(f"Data shape: {df.shape}")
        print(f"First few rows:\n{df.head()}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        features = []
        for idx, row in df.iterrows():
            try:
                # Get longitude and latitude
                lon = pd.to_numeric(row['Longitude'], errors='coerce')
                lat = pd.to_numeric(row['Latitude'], errors='coerce')
                
                # Skip rows without valid coordinates
                if pd.isna(lat) or pd.isna(lon):
                    print(f"Row {idx}: Skipping - missing coordinates")
                    continue
                
                # Validate coordinates
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    print(f"Row {idx}: Invalid coordinates: lat={lat}, lon={lon}")
                    continue
                
                # Create properties from all columns except Longitude/Latitude
                properties = {}
                for col in df.columns:
                    if col not in ['Longitude', 'Latitude']:
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
        
        print(f"\nSuccessfully created GeoJSON with {len(features)} features")
        return geojson
        
    except Exception as e:
        print(f"Error fetching or processing data: {e}")
        return {"type": "FeatureCollection", "features": []}
    finally:
        # Clean up temp file
        if os.path.exists('temp_data.csv'):
            os.remove('temp_data.csv')

def main():
    # Fetch and convert data
    geojson_data = fetch_and_convert_to_geojson()
    
    # Save to file
    output_path = 'public/marathons.geojson'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nGeoJSON saved to {output_path}")
    print(f"Total features: {len(geojson_data['features'])}")

if __name__ == "__main__":
    main()
