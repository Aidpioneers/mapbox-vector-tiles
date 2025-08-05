#!/usr/bin/env python3

import requests
import pandas as pd
import json
import os
from typing import Dict, Any

def fetch_and_convert_solar() -> Dict[str, Any]:
    """Fetch solar data and convert to GeoJSON"""
    url = "https://docs.google.com/spreadsheets/d/1Kx_K2B0Xf8OkQjE0QjO3QR7NfZf9X1F7Q9W9F1Z1Q9Q/export?format=csv&gid=0"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save raw CSV for debugging
        with open('solar_data.csv', 'w') as f:
            f.write(response.text)
        
        # Read CSV with pandas
        df = pd.read_csv('solar_data.csv')
        
        print(f"Solar data columns: {df.columns.tolist()}")
        print(f"Solar data shape: {df.shape}")
        print(f"First few rows:\n{df.head()}")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Find latitude and longitude columns (flexible naming)
        lat_col = None
        lon_col = None
        
        for col in df.columns:
            if 'lat' in col.lower():
                lat_col = col
            elif 'lon' in col.lower() or 'lng' in col.lower():
                lon_col = col
        
        if not lat_col or not lon_col:
            print(f"Could not find lat/lon columns in: {df.columns.tolist()}")
            return {"type": "FeatureCollection", "features": []}
        
        # Filter out rows with missing coordinates
        df = df.dropna(subset=[lat_col, lon_col])
        
        # Convert to numeric
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        
        # Drop rows with invalid coordinates
        df = df.dropna(subset=[lat_col, lon_col])
        
        # Filter by show column if it exists
        if 'show' in df.columns:
            df['show'] = df['show'].astype(str).str.upper().str.strip()
            df = df[df['show'] == 'TRUE']
        
        features = []
        for _, row in df.iterrows():
            # Create properties from all columns except lat/lon
            properties = {}
            for col in df.columns:
                if col not in [lat_col, lon_col]:
                    properties[col] = str(row[col]) if pd.notna(row[col]) else ""
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row[lon_col]), float(row[lat_col])]
                },
                "properties": properties
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
        
    except Exception as e:
        print(f"Error processing solar data: {e}")
        return {"type": "FeatureCollection", "features": []}

def fetch_and_convert_medical() -> Dict[str, Any]:
    """Fetch medical data and convert to GeoJSON"""
    url = "https://docs.google.com/spreadsheets/d/1Kx_K2B0Xf8OkQjE0QjO3QR7NfZf9X1F7Q9W9F1Z1Q9Q/export?format=csv&gid=1234567890"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save raw CSV for debugging
        with open('medical_data.csv', 'w') as f:
            f.write(response.text)
        
        # Read CSV with pandas
        df = pd.read_csv('medical_data.csv')
        
        print(f"Medical data columns: {df.columns.tolist()}")
        print(f"Medical data shape: {df.shape}")
        print(f"First few rows:\n{df.head()}")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Find latitude and longitude columns (flexible naming)
        lat_col = None
        lon_col = None
        
        for col in df.columns:
            if 'lat' in col.lower():
                lat_col = col
            elif 'lon' in col.lower() or 'lng' in col.lower():
                lon_col = col
        
        if not lat_col or not lon_col:
            print(f"Could not find lat/lon columns in: {df.columns.tolist()}")
            return {"type": "FeatureCollection", "features": []}
        
        # Filter out rows with missing coordinates
        df = df.dropna(subset=[lat_col, lon_col])
        
        # Convert to numeric
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        
        # Drop rows with invalid coordinates
        df = df.dropna(subset=[lat_col, lon_col])
        
        # Filter by show column if it exists
        if 'show' in df.columns:
            df['show'] = df['show'].astype(str).str.upper().str.strip()
            df = df[df['show'] == 'TRUE']
        
        features = []
        for _, row in df.iterrows():
            # Create properties from all columns except lat/lon
            properties = {}
            for col in df.columns:
                if col not in [lat_col, lon_col]:
                    properties[col] = str(row[col]) if pd.notna(row[col]) else ""
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row[lon_col]), float(row[lat_col])]
                },
                "properties": properties
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
        
    except Exception as e:
        print(f"Error processing medical data: {e}")
        return {"type": "FeatureCollection", "features": []}

def main():
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    print("Fetching solar data...")
    solar_geojson = fetch_and_convert_solar()
    
    print("Fetching medical data...")
    medical_geojson = fetch_and_convert_medical()
    
    # Save individual files
    with open('data/solar.geojson', 'w') as f:
        json.dump(solar_geojson, f, indent=2)
    
    with open('data/medical.geojson', 'w') as f:
        json.dump(medical_geojson, f, indent=2)
    
    # Combine all features
    combined_features = solar_geojson['features'] + medical_geojson['features']
    combined_geojson = {
        "type": "FeatureCollection",
        "features": combined_features
    }
    
    with open('data/combined.geojson', 'w') as f:
        json.dump(combined_geojson, f, indent=2)
    
    print(f"Generated {len(solar_geojson['features'])} solar features")
    print(f"Generated {len(medical_geojson['features'])} medical features")
    print(f"Combined {len(combined_features)} total features")

if __name__ == "__main__":
    main()
