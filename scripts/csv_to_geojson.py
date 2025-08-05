import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import json
import requests
from datetime import datetime
import os

def clean_numeric(value):
    """Clean and convert numeric values"""
    if pd.isna(value) or value == '':
        return 0
    return float(str(value).replace(',', '').replace('€', '').replace(' ', '')) or 0

def fetch_and_convert_solar():
    """Fetch solar data and convert to GeoJSON"""
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTJsNnPxAHbTwpovOYffeCdbZoVHBJzJI6vIWqvsV6Zj6S9PK0wpkUyoo27bXW8QxOaalujL_6VlfFP/pub?gid=1234705142&single=true&output=csv'
    
    df = pd.read_csv(url)
    
    # Filter only rows where show? = TRUE
    df = df[df['show?'].str.upper().str.strip() == 'TRUE']
    
    # Clean coordinates
    df = df.dropna(subset=['lat', 'lon'])
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])
    
    # Clean numeric fields
    df['savings'] = df['Gross cost savings'].apply(clean_numeric)
    df['investment'] = df['Total Investment'].apply(clean_numeric)
    df['system_size'] = df['System Size (kWp)'].apply(clean_numeric)
    df['co2_savings'] = df['CO2 Savings (t)'].apply(clean_numeric)
    df['treatments'] = df['Additional treatments / students'].apply(clean_numeric)
    
    # Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    
    # Select and rename columns for the final output
    gdf_clean = gdf[['geometry', 'Project Name Mapping', 'Partner Org', 'savings', 
                     'investment', 'system_size', 'co2_savings', 'treatments', 'Photos']].copy()
    gdf_clean.columns = ['geometry', 'name', 'partner', 'savings', 'investment', 
                        'system_size', 'co2_savings', 'treatments', 'photos']
    gdf_clean['type'] = 'solar'
    
    return gdf_clean

def fetch_and_convert_medical():
    """Fetch medical data and convert to GeoJSON"""
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSwQfNVeLSL33IGytiDNV8DAduygRZ5xC0EBI1JLzrgjEFeKANCDTcQ9m9AcWgjtSOec5UcBUvOH_fW/pub?gid=1455555915&single=true&output=csv'
    
    df = pd.read_csv(url)
    
    # Filter only rows where show? = TRUE
    df = df[df['show?'].str.upper().str.strip() == 'TRUE']
    
    # Clean coordinates
    df = df.dropna(subset=['lat', 'lon'])
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])
    
    # Clean quantity
    df['quantity'] = df['Total item quantity'].apply(clean_numeric)
    
    # Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    
    # Select and rename columns
    gdf_clean = gdf[['geometry', 'Safe hospital names', 'Shipment ID (unique)', 
                     'CURE ID (unique)', 'Shipment period (unique)', 'Number of beds (unique)',
                     'quantity', 'Type of medical institution (unique)', 'Photos']].copy()
    gdf_clean.columns = ['geometry', 'name', 'shipment_id', 'cure_id', 'shipment_date', 
                        'beds', 'quantity', 'institution_type', 'photos']
    gdf_clean['type'] = 'medical'
    
    return gdf_clean

def main():
    """Main function to process data and save GeoJSON"""
    print("Fetching solar data...")
    solar_gdf = fetch_and_convert_solar()
    
    print("Fetching medical data...")
    medical_gdf = fetch_and_convert_medical()
    
    # Combine datasets
    print("Combining datasets...")
    combined_gdf = pd.concat([solar_gdf, medical_gdf], ignore_index=True)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save individual GeoJSON files
    solar_gdf.to_file('data/solar.geojson', driver='GeoJSON')
    medical_gdf.to_file('data/medical.geojson', driver='GeoJSON')
    combined_gdf.to_file('data/combined.geojson', driver='GeoJSON')
    
    print(f"Processed {len(solar_gdf)} solar projects")
    print(f"Processed {len(medical_gdf)} medical projects")
    print(f"Total: {len(combined_gdf)} projects")
    print("GeoJSON files saved to data/ directory")

if __name__ == "__main__":
    main()
