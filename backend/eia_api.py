"""
EIA API integration for oil and gas data
Fetches production statistics for Montana
"""

import httpx
from typing import Optional, Dict, List
import asyncio

EIA_API_KEY = "6T4tHNwYj5gfJ2neZXzf7h6ucFoTFA7UnFWh0heM"
EIA_BASE_URL = "https://api.eia.gov/v2"

# Montana state code
MONTANA_STATE_CODE = "MT"

async def fetch_eia_data(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Fetch data from EIA API

    Args:
        endpoint: API endpoint path
        params: Additional query parameters

    Returns:
        JSON response data or None if error
    """
    url = f"{EIA_BASE_URL}/{endpoint}"

    # Fetch data without area filter to get whatever is available
    default_params = {
        "api_key": EIA_API_KEY,
        "frequency": "monthly",
        "data[0]": "value",
        "start": "2024-01",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 12  # Last 12 months
    }

    if params:
        default_params.update(params)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=default_params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"EIA API error for {endpoint}: {e}")
        return None


async def get_crude_oil_production() -> Optional[Dict]:
    """Get crude oil production data for PADD 2 (includes Montana)"""
    return await fetch_eia_data("petroleum/crd/crpdn/data")


async def get_proved_reserves() -> Optional[Dict]:
    """Get proved reserves data for PADD 2 (includes Montana)"""
    return await fetch_eia_data("petroleum/crd/pres/data")


async def get_drilling_activity() -> Optional[Dict]:
    """Get drilling activity and well counts for PADD 2 (includes Montana)"""
    return await fetch_eia_data("petroleum/crd/drill/data")


async def get_footage_drilled() -> Optional[Dict]:
    """Get footage drilled data for PADD 2 (includes Montana)"""
    return await fetch_eia_data("petroleum/crd/wellfoot/data")


async def get_well_costs() -> Optional[Dict]:
    """Get well drilling costs for PADD 2 (includes Montana)"""
    return await fetch_eia_data("petroleum/crd/wellcost/data")


async def get_lease_condensate() -> Optional[Dict]:
    """Get crude oil plus lease condensate reserves and production"""
    return await fetch_eia_data("petroleum/crd/cplc/data")


async def get_nonproducing_reserves() -> Optional[Dict]:
    """Get proved nonproducing reserves"""
    return await fetch_eia_data("petroleum/crd/nprod/data")


async def get_api_gravity() -> Optional[Dict]:
    """Get crude oil production by API gravity"""
    return await fetch_eia_data("petroleum/crd/api/data")


async def get_gulf_offshore() -> Optional[Dict]:
    """Get Gulf of America federal offshore production"""
    return await fetch_eia_data("petroleum/crd/gom/data")


async def get_exploratory_wells() -> Optional[Dict]:
    """Get exploratory and development wells"""
    return await fetch_eia_data("petroleum/crd/wellend/data")


async def get_seismic_crews() -> Optional[Dict]:
    """Get maximum active seismic crew counts"""
    return await fetch_eia_data("petroleum/crd/seis/data")


async def get_well_depth() -> Optional[Dict]:
    """Get average depth of wells drilled"""
    return await fetch_eia_data("petroleum/crd/welldep/data")


async def get_all_montana_data() -> Dict:
    """
    Fetch all requested EIA data categories for Montana/PADD 2

    Returns:
        Dictionary with all data categories
    """
    # Run all requests in parallel
    results = await asyncio.gather(
        get_crude_oil_production(),
        get_proved_reserves(),
        get_lease_condensate(),
        get_nonproducing_reserves(),
        get_api_gravity(),
        get_gulf_offshore(),
        get_drilling_activity(),
        get_exploratory_wells(),
        get_seismic_crews(),
        get_footage_drilled(),
        get_well_depth(),
        get_well_costs(),
        return_exceptions=True
    )

    return {
        "crude_oil_production": results[0] if not isinstance(results[0], Exception) else None,
        "proved_reserves": results[1] if not isinstance(results[1], Exception) else None,
        "lease_condensate": results[2] if not isinstance(results[2], Exception) else None,
        "nonproducing_reserves": results[3] if not isinstance(results[3], Exception) else None,
        "api_gravity": results[4] if not isinstance(results[4], Exception) else None,
        "gulf_offshore": results[5] if not isinstance(results[5], Exception) else None,
        "drilling_activity": results[6] if not isinstance(results[6], Exception) else None,
        "exploratory_wells": results[7] if not isinstance(results[7], Exception) else None,
        "seismic_crews": results[8] if not isinstance(results[8], Exception) else None,
        "footage_drilled": results[9] if not isinstance(results[9], Exception) else None,
        "well_depth": results[10] if not isinstance(results[10], Exception) else None,
        "well_costs": results[11] if not isinstance(results[11], Exception) else None,
    }


async def get_montana_power_plants() -> Optional[Dict]:
    """
    Fetch all electricity-generating power plants in Montana.

    Uses the EIA Form 860 generator data which includes:
    - Plant name and ID
    - Location (latitude/longitude)
    - Technology type (e.g., Conventional Hydroelectric, Solar Photovoltaic)
    - Nameplate capacity in megawatts (MW)

    Returns:
        Dictionary containing power plant data or None if error
    """
    # EIA API v2 endpoint for generator data (Form 860)
    endpoint = "electricity/operating-generator-capacity/data"

    # Try multiple parameter combinations since the API can be finicky
    # IMPORTANT: Request latitude, longitude, and capacity as data columns
    param_sets = [
        # Try 1: Annual frequency with coordinates and capacity
        {
            "api_key": EIA_API_KEY,
            "frequency": "annual",
            "data[0]": "latitude",
            "data[1]": "longitude",
            "data[2]": "nameplate-capacity-mw",
            "facets[stateid][]": "MT",
            "offset": 0,
            "length": 5000
        },
        # Try 2: Monthly with specific period and all location/capacity fields
        {
            "api_key": EIA_API_KEY,
            "frequency": "monthly",
            "data[0]": "latitude",
            "data[1]": "longitude",
            "data[2]": "nameplate-capacity-mw",
            "data[3]": "county",
            "facets[stateid][]": "MT",
            "start": "2023-01",
            "end": "2024-12",
            "offset": 0,
            "length": 5000
        },
        # Try 3: Just the most recent monthly data with all fields
        {
            "api_key": EIA_API_KEY,
            "frequency": "monthly",
            "data[0]": "latitude",
            "data[1]": "longitude",
            "data[2]": "nameplate-capacity-mw",
            "facets[stateid][]": "MT",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": 0,
            "length": 5000
        }
    ]

    url = f"{EIA_BASE_URL}/{endpoint}"

    for i, params in enumerate(param_sets):
        try:
            print(f"Attempting power plant query #{i+1}...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Check if we got any data
                if data and data.get("response", {}).get("data"):
                    print(f"Success! Got {len(data['response']['data'])} generator records")
                    return data
                else:
                    print(f"Query #{i+1} returned no data")
        except Exception as e:
            print(f"Query #{i+1} failed: {e}")
            continue

    print("All query attempts failed for Montana power plants")
    return None


def format_power_plant_data(data: Dict) -> List[Dict]:
    """
    Format power plant data from EIA API response into clean structure.

    Args:
        data: Raw EIA API response containing generator data

    Returns:
        List of dictionaries with plant information including:
        - plant_name: Name of the power plant
        - plant_id: EIA plant identifier
        - latitude: Plant latitude coordinate (may be None if not in API response)
        - longitude: Plant longitude coordinate (may be None if not in API response)
        - technology: Type of generation technology
        - capacity_mw: Nameplate capacity in megawatts
        - county: County where plant is located
        - balancing_authority: Grid operator
    """
    if not data or "response" not in data:
        return []

    response = data.get("response", {})
    generators = response.get("data", [])

    if not generators:
        return []

    # Debug: Print first generator to see available fields
    print(f"Sample generator fields: {list(generators[0].keys())[:20]}")

    # Process and deduplicate by plant
    plants = {}
    for gen in generators:
        plant_id = gen.get("plantid")
        if not plant_id:
            continue

        if plant_id not in plants:
            plants[plant_id] = {
                "plant_id": plant_id,
                "plant_name": gen.get("plantName", "Unknown"),
                "latitude": gen.get("latitude"),  # Now requested via data[] parameter
                "longitude": gen.get("longitude"),  # Now requested via data[] parameter
                "technology": gen.get("technology", "Unknown"),
                "capacity_mw": 0.0,  # Will aggregate from nameplate-capacity-mw
                "county": gen.get("county", ""),
                "balancing_authority": gen.get("balancing_authority_code", ""),
                "status": gen.get("status", ""),
                "statusDescription": gen.get("statusDescription", ""),
                "primary_fuel": gen.get("energy_source_code", ""),
                "sector": gen.get("sector", ""),
                "state": gen.get("stateName", "Montana")
            }

        # Aggregate nameplate capacity in megawatts
        capacity = gen.get("nameplate-capacity-mw")
        if capacity is not None:
            try:
                plants[plant_id]["capacity_mw"] += float(capacity)
            except (ValueError, TypeError):
                # If capacity isn't a valid number, just count the generator
                plants[plant_id]["capacity_mw"] += 1

    # Round capacity to 2 decimal places
    for plant in plants.values():
        plant["capacity_mw"] = round(plant["capacity_mw"], 2)

    print(f"Processed {len(plants)} unique power plants from {len(generators)} generators")
    return list(plants.values())


def format_eia_data_for_display(data: Dict) -> List[Dict]:
    """
    Format EIA API response for frontend display

    Args:
        data: Raw EIA API response

    Returns:
        List of formatted data points
    """
    if not data or "response" not in data:
        return []

    response = data.get("response", {})
    data_points = response.get("data", [])

    formatted = []
    for point in data_points:
        formatted.append({
            "period": point.get("period"),
            "value": point.get("value"),
            "units": response.get("units"),
            "series": point.get("series-description", "")
        })

    return formatted
