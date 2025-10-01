# Montana Oil Well Production Data Setup Guide

This guide will help you download production data from DNRC and integrate it into the map.

## Step 1: Download Production Data from DNRC

### Option A: Monthly Production by Well (Recommended)
1. Go to: https://bogapps.dnrc.mt.gov/dataminer/Production/ProductionByWell.aspx
2. Leave search fields empty to get all wells
3. Click "Search"
4. Click "Text" export button (more reliable than Excel)
5. Save the text file as `production_data.txt` in the `data/production/` folder

### Option B: Cumulative Production
1. Go to: https://bogapps.dnrc.mt.gov/dataminer/Production/ProdCumField.aspx
2. Export all fields to get cumulative data
3. Save as `production_cumulative.txt`

### Data Format Expected
The exported file should contain columns like:
- API Number
- Well Name
- Operator
- Production Month/Year
- Oil Production (BBL)
- Gas Production (MCF)
- Water Production (BBL)

## Step 2: Import Data into SQLite Database

Once you have the data file:

```bash
cd backend
python import_production.py ../data/production/production_data.txt
```

This will:
- Parse the production data
- Create a SQLite database at `backend/production.db`
- Calculate barrels per day for each well
- Index by API number for fast lookups

## Step 3: Backend Setup

The backend is already configured to serve production data from the database.
Restart the backend server:

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

## Step 4: Test

Open the map and click on any oil well marker. You should see:
- Oil production (BBL/day)
- Gas production (MCF/day)
- Cumulative totals
- Latest production month

## Notes

- Production data needs to be updated manually when new monthly data is released
- Data is typically 1-2 months behind current month
- Database updates can be done by re-running the import script
- Contact MBOGC at (406) 656-0040 for data questions

## Alternative: Request Bulk Data

You can also contact MBOGC directly to request a bulk data dump:
- Email: [email protected]
- Phone: (406) 656-0040
- They may be able to provide a full database export