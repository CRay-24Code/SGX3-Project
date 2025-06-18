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


if __name__ == "__main__":
    load_traffic_data()  # <- This runs BEFORE the server starts
    app.run(debug=True, host="0.0.0.0", port=8031)
