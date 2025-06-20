#SGX3 Coding Institute Repo

# SGX3-Project

## Description

This project contains a Flask API for analyzing Austin traffic data and a Python script to consume data from the API. The API provides various endpoints to query, filter, and summarize traffic incident data, including functionalities to analyze traffic hazards by year and hour.

## Features

- **Flask API**: Exposes endpoints for traffic data analysis.
- **Data Loading**: Loads traffic data from `atxtraffic.csv`.
- **Data Exploration**: Endpoints to view data head, shape, columns, and summary statistics.
- **Traffic Hazard Analysis**: Filter traffic incidents by year and count traffic hazards.
- **Time-based Filtering**: Filter traffic data by hour and hour ranges.
- **Haversine Calculation**: Includes a utility function for calculating distances between geographical coordinates.
- **API Consumer**: A Python script (`consumer.py`) to demonstrate interaction with the deployed API.

## Installation

To set up this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CRay-24Code/SGX3-Project.git
   cd SGX3-Project
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install Flask pandas numpy requests
   ```

4. **Data File:**
   Ensure `atxtraffic.csv` is present in the project root directory. This file is essential for the Flask application to load the traffic data.

## Usage

### Running the Flask API (`app.py`)

To start the Flask API server:

```bash
python app.py
```

The API will run on `http://127.0.0.1:5000/` by default. You can then access the various endpoints.

### Using the API Consumer (`consumer.py`)

The `consumer.py` script demonstrates how to interact with a deployed instance of the Flask API. Before running `consumer.py`, ensure the API is running and accessible at the specified URL (currently `http://35.206.76.195:8031`).

To run the consumer script:

```bash
python consumer.py
```

This script queries the `/rush_hour_nearby` endpoint with predefined latitude, longitude, and year, and prints the response.

## API Endpoints

The `app.py` Flask application exposes the following endpoints:

- **`/` (GET)**: Returns the first 10 rows of the traffic data as a JSON array.
- **`/head?count=<num>` (GET)**: Returns the first `<num>` rows of the traffic data.
- **`/shape` (GET)**: Returns the number of rows and columns in the dataset.
- **`/columns` (GET)**: Returns a list of all column names in the dataset.
- **`/summary` (GET)**: Provides a summary of the dataset, including total rows, total columns, and details for each column (name, data type, non-nulls, nulls).
- **`/describe` (GET)**: Returns descriptive statistics for the numerical columns in the dataset.
- **`/uniqueval?column=<column_name>` (GET)**: Returns unique values and their count for a specified column.
- **`/year` (GET)**: Returns a sorted list of unique years present in the 'Published Date' column.
- **`/hazard_count?year=<year>&full=<true/false>` (GET)**: Counts traffic hazards for a given year. If `full=true`, returns all matching reports.
- **`/hour` (GET)**: Returns the frequency of traffic incidents by hour of the day.
- **`/by_hour_range?start=<start_hour>&end=<end_hour>` (GET)**: Filters traffic data for incidents occurring within a specified hour range (0-23).
- **`/rush_hour_nearby?lat=<latitude>&lon=<longitude>&year=<year>` (GET)**: (Note: This endpoint is consumed by `consumer.py` but its implementation is not directly visible in `app.py`'s provided code snippet. It likely involves the `haversine` function for proximity calculations.)

## Data Source

The project utilizes `atxtraffic.csv`, which is expected to contain Austin traffic incident data. The `app.py` script processes this CSV file, extracting 'Year' and 'Hour' from a 'Published Date' column if available.

## License

This project is open-source and available under the MIT License. See the `LICENSE` file for more details.


