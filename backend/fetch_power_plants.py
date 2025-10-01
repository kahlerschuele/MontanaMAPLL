"""
Standalone script to fetch Montana power plant data from EIA API.

This script demonstrates how to:
1. Query the EIA API for electricity generator data
2. Filter for Montana power plants
3. Parse and display the data using pandas

Requirements:
    pip install requests pandas
"""

import requests
import pandas as pd
from typing import Optional

# EIA API configuration
# TODO: Replace with your own API key from https://www.eia.gov/opendata/register.php
EIA_API_KEY = "6T4tHNwYj5gfJ2neZXzf7h6ucFoTFA7UnFWh0heM"
EIA_BASE_URL = "https://api.eia.gov/v2"


def fetch_montana_power_plants() -> Optional[pd.DataFrame]:
    """
    Fetch all electricity-generating power plants in Montana from the EIA API.

    This function uses the EIA Form 860 generator data which includes:
    - Plant name and location
    - Geographic coordinates (latitude/longitude)
    - Technology type (e.g., Conventional Hydroelectric, Solar Photovoltaic, Wind)
    - Nameplate capacity in megawatts (MW)

    Returns:
        pandas DataFrame with power plant information, or None if error occurs
    """

    # Step 1: Construct the API endpoint URL
    # We're using the 'operating-generator-capacity' endpoint which provides Form 860 data
    endpoint = "electricity/operating-generator-capacity/data"
    url = f"{EIA_BASE_URL}/{endpoint}"

    # Step 2: Set up query parameters to filter for Montana generators
    # Note: Generator data is available monthly, we'll get the most recent data
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "monthly",             # Generator data updates monthly
        "facets[stateid][]": "MT",          # Filter for Montana (MT)
        "sort[0][column]": "period",        # Sort by time period
        "sort[0][direction]": "desc",       # Most recent first
        "offset": 0,                        # Start at first record
        "length": 5000                      # Max records to return (ensure we get all generators)
    }

    try:
        # Step 3: Make the API request
        print(f"Fetching Montana power plant data from EIA API...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raise error for bad status codes

        # Step 4: Parse the JSON response
        data = response.json()

        if not data or "response" not in data:
            print("Error: Invalid response format from API")
            return None

        # Extract the generator records from the response
        generators = data.get("response", {}).get("data", [])

        if not generators:
            print("No generator data found for Montana")
            return None

        print(f"Retrieved {len(generators)} generator records")

        # Step 5: Convert to pandas DataFrame for easy analysis
        df = pd.DataFrame(generators)

        # Step 6: Select and rename relevant columns for clarity
        columns_to_keep = {
            "plantid": "plant_id",
            "plantName": "plant_name",
            "latitude": "latitude",
            "longitude": "longitude",
            "technology": "technology_type",
            "nameplate-capacity-mw": "capacity_mw",
            "county": "county",
            "balancing_authority_code": "grid_operator",
            "status": "operational_status",
            "energy_source_code": "primary_fuel"
        }

        # Keep only columns that exist in the response
        available_columns = {k: v for k, v in columns_to_keep.items() if k in df.columns}
        df_cleaned = df[list(available_columns.keys())].copy()
        df_cleaned.rename(columns=available_columns, inplace=True)

        # Step 7: Convert capacity to numeric and aggregate by plant
        # (Some plants have multiple generators, so we'll sum their capacities)
        if "capacity_mw" in df_cleaned.columns:
            df_cleaned["capacity_mw"] = pd.to_numeric(df_cleaned["capacity_mw"], errors="coerce")

        # Group by plant to get total capacity per facility
        if "plant_id" in df_cleaned.columns:
            df_aggregated = df_cleaned.groupby("plant_id").agg({
                "plant_name": "first",
                "latitude": "first",
                "longitude": "first",
                "technology_type": "first",
                "capacity_mw": "sum",  # Sum capacities for plants with multiple generators
                "county": "first",
                "grid_operator": "first",
                "operational_status": "first",
                "primary_fuel": "first"
            }).reset_index()

            # Round capacity to 2 decimal places
            df_aggregated["capacity_mw"] = df_aggregated["capacity_mw"].round(2)

            # Sort by capacity (largest first)
            df_aggregated = df_aggregated.sort_values("capacity_mw", ascending=False)

            return df_aggregated

        return df_cleaned

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from EIA API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def main():
    """
    Main function to fetch and display Montana power plant data.
    """
    print("=" * 80)
    print("Montana Electricity-Generating Power Plants")
    print("Data Source: U.S. Energy Information Administration (EIA) Form 860")
    print("=" * 80)
    print()

    # Fetch the data
    df = fetch_montana_power_plants()

    if df is None or df.empty:
        print("Failed to retrieve power plant data")
        return

    # Display summary statistics
    print(f"\nTotal number of power plants in Montana: {len(df)}")
    print(f"Total generating capacity: {df['capacity_mw'].sum():.2f} MW")
    print()

    # Show technology breakdown
    if "technology_type" in df.columns:
        print("\nCapacity by Technology Type:")
        tech_summary = df.groupby("technology_type")["capacity_mw"].agg(["sum", "count"])
        tech_summary.columns = ["Total Capacity (MW)", "Number of Plants"]
        tech_summary = tech_summary.sort_values("Total Capacity (MW)", ascending=False)
        print(tech_summary.to_string())
        print()

    # Display first 10 rows
    print("\n" + "=" * 80)
    print("Sample Data: First 10 Power Plants (by capacity)")
    print("=" * 80)
    print(df.head(10).to_string(index=False))
    print()

    # Optionally save to CSV
    output_file = "montana_power_plants.csv"
    df.to_csv(output_file, index=False)
    print(f"\nFull dataset saved to: {output_file}")


if __name__ == "__main__":
    main()
