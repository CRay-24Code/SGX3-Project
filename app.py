from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import os

# Define your global DataFrame
traffic_df = None

app = Flask(__name__)

def load_traffic_data():
    global traffic_df
    print("Loading Austin Traffic Data...")
    traffic_df = pd.read_csv("atxtraffic.csv")
    print(f"Loaded {len(traffic_df)} rows into memory.")

    if "Published Date" in traffic_df.columns:
        traffic_df["Published Date"] = pd.to_datetime(traffic_df["Published Date"], errors ="coerce")
        traffic_df["Year"] = traffic_df["Published Date"].dt.year
        traffic_df["Hour"] = traffic_df["Published Date"].dt.hour
        print("Extracted 'Year' and 'Hour' from Published Date'.")
    else:
        print("Column 'Published Date' not found.")

    print(f"Loaded {len(traffic_df)} rows into memory.")


@app.route("/")
def index():      
    global traffic_df 
    sample = traffic_df.head(10).to_dict(orient="records")
    return jsonify(sample)

@app.route("/head")
def top():
    global traffic_df
    num = int(request.args.get('count'))
    sample = traffic_df.head(num).to_dict(orient="records")
    return jsonify(sample)

@app.route("/shape")
def shape():
    global traffic_df
    rows, col = traffic_df.shape
    return jsonify({"rows": rows, "columns": col})

@app.route("/columns")
def get_columns():
    global traffic_df
    columns = traffic_df.columns.tolist()
    return jsonify({"columns": columns})

@app.route("/summary")
def summary():
    global traffic_df
    
    info = {
            "total_rows": len(traffic_df),
            "total_columns": traffic_df.shape[1],
            "columns": []
            }

    for col in traffic_df.columns:
        info["columns"].append({
            "name": col,
            "dtype": str(traffic_df[col].dtype),
            "non_nulls": int(traffic_df[col].count()),
            "nulls": int(traffic_df.shape[0] - traffic_df[col].count())
            })

        return jsonify(info)

@app.route("/describe")
def describe():
    global traffic_df
    stats_df = traffic_df.describe()
    stats_dict = stats_df.to_dict()
    return jsonify(stats_dict)

@app.route("/uniqueval")
def unique_values():
    global traffic_df

    column = request.args.get("column",type=str)
    if column is None:
        return jsonify({"error": "Missing 'column' parameter"}), 400

    if column not in traffic_df.columns:
        return jsonify({"error": f"Column '{column}' not found"}), 400

    unique_vals = traffic_df[column].dropna().unique().tolist()
    return jsonify ({"column": column, "unique_value": unique_vals, "count": len(unique_vals) })

@app.route("/year")
def get_year():
    global traffic_df
    if "Year" not in traffic_df.columns:
        return jsonify({"error": "Year column not available"}), 500

    years = traffic_df["Year"].dropna().unique().tolist()
    years.sort()
    return jsonify({"years":years})

@app.route("/hazard_count")
def hazard_count_by_year():
    global traffic_df

    #Ensure the data is loaded
    if traffic_df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    year_param = request.args.get("year")
    full = request.args.get("full", "false").lower() == "true"

    if not year_param:
        return jsonify({"error": "Missing 'year' query parameter"}), 400

    try:
        year = int(year_param)
    except ValueError:
        return jsonify({"error": "Invalid year format"}), 400

    #Filter for the given year and Traffic Hazard
    filtered_df = traffic_df[
            (traffic_df["Year"] == year) &
            (traffic_df["Issue Reported"].str.contains("Traffic Hazard", na=False, case=False))
            ]

    result = {
            "year": year,
            "issue": "Traffic Hazard",
            "count": len(filtered_df)
            }

    if full:
        result["reports"] = filtered_df.to_dict(orient="records")

    return jsonify(result)

@app.route("/hour")
def get_hour():
    global traffic_df

    if "Hour" not in traffic_df.columns:
        return jsonify({"error": "'Hour' column not available"}), 500

    #Drop nulls, get frequency convert to dict
    hour_counts = (
            traffic_df["Hour"]
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
            .to_dict()
            )
    return jsonify({"hour_frequencies": hour_counts})

@app.route("/by_hour_range")
def filter_by_hour_range():
    global traffic_df

    #validate that the data is loaded
    if traffic_df is None or "Hour" not in traffic_df.columns:
        return jsonify({"error": "Data not loaded or 'Hour' column missing"}), 500

    start_hour = request.args.get("start")
    end_hour = request.args.get("end")

    if start_hour is None or end_hour is None:
        return jsonify({"error": "Missing 'start' or 'end' hour parameter"}), 400

    #validate input is integer and within 0-23
    try:
        start_hour = int(start_hour)
        end_hour = int(end_hour)
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError
    except ValueError:
            return jsonify({"error": "Hour must be integers between 0 and 23"}), 400

    # Filter data between the given hours
    filtered_df = traffic_df[
        (traffic_df["Hour"] >= start_hour) &
        (traffic_df["Hour"] <= end_hour)
    ]

    results = filtered_df.to_dict(orient="records")

    return jsonify({
        "start_hour": start_hour,
        "end_hour": end_hour,
        "count": len(results),
        "records": results
    })

def haversine(lat1, lon1, lat2, lon2):
    #Radius of earth in kilometers
    R = 6371.0
    #Convert degrees to radius
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    #Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c #Distance in kilometers

@app.route("/nearby_incidents")
def nearby_incidents():
    global traffic_df

    if "Latitude" not in traffic_df.columns or "Longitude" not in traffic_df.columns:
        return jsonify({"error": "Latitude/Longitude columns missing"}), 500

    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing 'lat' or 'lon' query parameters"}), 400

    #Drop rows with missing coordinates
    df = traffic_df.dropna(subset=["Latitude", "Longitude"]).copy()

    #Compare distance
    df["Distance_km"] = haversine(lat, lon, df["Latitude"], df["Longitude"])

    #Filter within 1 km
    nearby_df = df[df["Distance_km"] <= 1]

    return jsonify({
        "input_location": {"lat": lat, "lon": lon},
        "count": len(nearby_df),
        "records": nearby_df.to_dict(orient="records")
        })

@app.route("/cleaned_geo")
def cleaned_geo():
    global traffic_df

    if traffic_df is None:
        return jsonify({"error": "Data not loaded"}), 500

    #Apply the filtering
    cleaned_df = traffic_df[
            (traffic_df["Latitude"] != 0) &
            (traffic_df["Longitude"] != 0) &
            (traffic_df["Latitude"] <= 35)
            ]

    #Convert to JSON
    records = cleaned_df.to_dict(orient="records")

    return jsonify({
        "original_count": len(traffic_df),
        "filtered_count": len(cleaned_df),
        "records": records
        })

@app.route("/rush_hour")
def rush_hour():
    global traffic_df

    if traffic_df is None:
        return jsonify({"error": "Data not loaded"}), 500

    if "Hour" not in traffic_df.columns:
        return jsonify({"error": "'Hour' column not available"}), 500

    #Create a boolean mask for rush hour
    traffic_df["rush_hour"] = (
            ((traffic_df["Hour"] >= 7) & (traffic_df["Hour"] <= 9)) |
            ((traffic_df["Hour"] >= 16) & (traffic_df["Hour"] <= 18))
            )

    #Filter just the rush hour records
    rush_df = traffic_df[traffic_df["rush_hour"] == True]

    return jsonify({
        "count": len(rush_df),
        "rush_hour_records": rush_df.to_dict(orient="records")
        })

@app.route("/rush_hour_nearby")
def rush_hour_nearby():
    global traffic_df

    if traffic_df is None:
        return jsonify({"error": "Data not loaded"}), 500

    #Get query parameters
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
        year = int(request.args.get("year"))
    except (TypeError, ValueError):
        return jsonify({"error": "Missing or invalid 'lat', 'lon', or 'year' parameters"}), 400

    #Ensure required columns are present
    if not all(col in traffic_df.columns for col in ["Latitude", "Longitude", "Hour", "Year"]):
        return jsonify({"error": "Missing necessary columns in data"}), 500

    #Filter out bad/missing coordinates
    df = traffic_df[
            (traffic_df["Latitude"].notnull()) &
            (traffic_df["Longitude"].notnull()) &
            (traffic_df["Latitude"] != 0) &
            (traffic_df["Longitude"] != 0)
            ].copy()

    #Ensure 'rush hour' column exists
    if "rush_hour" not in df.columns:
        df["rush_hour"] = (
                ((df["Hour"] >= 7) & (df["Hour"] <= 9)) |
                ((df["Hour"] >= 16) & (df["Hour"] <= 18))
                )

    #Compute distance
    df["distance_km"] = haversine(lat, lon, df["Latitude"], df["Longitude"])

    #Filter: within 1 km, rush hour, specific year
    filtered = df[
            (df["distance_km"] <= 1.0) &
            (df["rush_hour"] == True) &
            (df["Year"] == year)
            ]

    return jsonify({
        "input_location": {"latitude": lat, "longitude": lon},
        "year": year,
        "count": len(filtered),
        "records": filtered.to_dict(orient="records")
        })

if __name__ == "__main__":
    load_traffic_data()  # <- This runs BEFORE the server starts
    app.run(debug=True, host="0.0.0.0", port=8031)
