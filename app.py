from flask import Flask, jsonify, request
import pandas as pd
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
        print("Extracted 'Year' from Published Date'.")
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
    count = len(filtered_df)

    return jsonify({
        "year": year,
        "issue": "Traffic Hazard",
        "count": count
        })



if __name__ == "__main__":
    load_traffic_data()  # <- This runs BEFORE the server starts
    app.run(debug=True, host="0.0.0.0", port=8031)
