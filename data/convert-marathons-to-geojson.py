#!/usr/bin/env python3
"""
Convert marathons CSV data to GeoJSON format for use with the map component.
"""

import csv
import json
import sys
from datetime import datetime

def clean_coordinate(coord_str):
    """Clean and convert coordinate string to float."""
    if not coord_str or coord_str.strip() == '':
        return None
    
    # Replace unicode minus signs with regular minus
    coord_str = coord_str.replace('−', '-')
    
    try:
        return float(coord_str.strip())
    except ValueError:
        return None

def clean_text(text):
    """Clean text by removing extra whitespace and handling encoding."""
    if not text:
        return ""
    
    # Handle common encoding issues
    text = text.replace('Ã©', 'é')  # Fix é character
    text = text.replace('Ã¨', 'è')  # Fix è character  
    text = text.replace('Ã¡', 'á')  # Fix á character
    text = text.replace('Ã­', 'í')  # Fix í character
    text = text.replace('Ã³', 'ó')  # Fix ó character
    text = text.replace('Ã¼', 'ü')  # Fix ü character
    text = text.replace('Ã±', 'ñ')  # Fix ñ character
    text = text.replace('Ã§', 'ç')  # Fix ç character
    text = text.replace('â€™', "'")  # Fix apostrophe
    text = text.replace('â€œ', '"')  # Fix left quote
    text = text.replace('â€', '"')   # Fix right quote
    text = text.replace('â€"', '–')  # Fix en dash
    text = text.replace('â€"', '—')  # Fix em dash
    
    return text.strip()

def parse_date(date_str):
    """Parse date string to ISO format."""
    if not date_str or date_str.strip() == '':
        return None
    
    date_str = date_str.strip()
    
    # Handle various date formats
    try:
        # Try DD/MM/YYYY format first
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Try other formats as needed
        return date_str
    except:
        return date_str

def convert_csv_to_geojson(csv_file_path, geojson_file_path):
    """Convert CSV file to GeoJSON format."""
    
    features = []
    skipped_count = 0
    processed_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
            # Skip if show? is not TRUE
            show_value = row.get('show?', '').strip().upper()
            if show_value != 'TRUE':
                skipped_count += 1
                continue
            
            # Get coordinates
            lat_str = row.get('lat', '').strip()
            lon_str = row.get('lon', '').strip()
            
            lat = clean_coordinate(lat_str)
            lon = clean_coordinate(lon_str)
            
            # Skip if coordinates are invalid
            if lat is None or lon is None:
                skipped_count += 1
                print(f"Row {row_num}: Skipping due to invalid coordinates: lat='{lat_str}', lon='{lon_str}'")
                continue
            
            # Skip if essential fields are missing
            name = clean_text(row.get('Name', ''))
            city = clean_text(row.get('City', ''))
            
            if not name or name == '#REF!' or not city or city == '#REF!':
                skipped_count += 1
                print(f"Row {row_num}: Skipping due to missing/invalid name or city")
                continue
            
            # Create feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "type": "marathon",
                    "name": name,
                    "city": city,
                    "country_iso": clean_text(row.get('ISO3', '')),
                    "year": clean_text(row.get('Year', '')),
                    "marathon_type": clean_text(row.get('Full / Half', '')),
                    "date": parse_date(row.get('Date', '')),
                    "signup_deadline": parse_date(row.get('Sign up deadlines', '')),
                    "availability": clean_text(row.get('Availability', '')),
                    "landing_page": clean_text(row.get('Landing Page', '')),
                    "google_ads": clean_text(row.get('Google Ads', '')),
                    "comments": clean_text(row.get('Comments', '')),
                    "map_info_text": clean_text(row.get('Map Info Text', ''))
                }
            }
            
            features.append(feature)
            processed_count += 1
    
    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Write to file
    with open(geojson_file_path, 'w', encoding='utf-8') as geojsonfile:
        json.dump(geojson, geojsonfile, indent=2, ensure_ascii=False)
    
    print(f"Conversion complete!")
    print(f"Processed: {processed_count} records")
    print(f"Skipped: {skipped_count} records")
    print(f"Output: {geojson_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert-marathons-to-geojson.py <input.csv> <output.geojson>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    geojson_file = sys.argv[2]
    
    convert_csv_to_geojson(csv_file, geojson_file)
