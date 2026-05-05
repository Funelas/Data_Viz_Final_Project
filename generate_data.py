import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# 1. Barangays Data
barangays_list = [
    "Poblacion", "San Antonio", "San Jose", "San Vicente", "Santo Niño", 
    "Platero", "Tubigan", "Canlalay", "De La Paz", "Casile", 
    "Malaban", "Soro-Soro", "Timbao", "Loma", "Zapote", 
    "Mamplasan", "Ganado", "Langkiwa", "Bungahan", "San Francisco (Halang)",
    "Calabuso", "Santo Tomas"
]

# Hardcoded GPS coordinates for Biñan Barangays
brgy_coords = {
    "Poblacion": (14.3370, 121.0850),
    "San Antonio": (14.3360, 121.0880),
    "San Jose": (14.3430, 121.0820),
    "San Vicente": (14.3320, 121.0810),
    "Santo Niño": (14.3350, 121.0860),
    "Platero": (14.3230, 121.0820),
    "Tubigan": (14.3200, 121.0760),
    "Canlalay": (14.3420, 121.0720),
    "De La Paz": (14.3480, 121.0840),
    "Casile": (14.3440, 121.0860),
    "Malaban": (14.3460, 121.0880),
    "Soro-Soro": (14.3290, 121.0780),
    "Timbao": (14.2950, 121.0500),
    "Loma": (14.2900, 121.0400),
    "Zapote": (14.3180, 121.0790),
    "Mamplasan": (14.3090, 121.0750),
    "Ganado": (14.2980, 121.0740),
    "Langkiwa": (14.2880, 121.0600),
    "Bungahan": (14.2850, 121.0680),
    "San Francisco (Halang)": (14.3010, 121.0650),
    "Calabuso": (14.2850, 121.0550),
    "Santo Tomas": (14.3150, 121.0700)
}

barangays_data = []
for brgy in barangays_list:
    pop = np.random.randint(5000, 35000)
    lat, lon = brgy_coords[brgy]
    
    # Malaban, Casile, De La Paz are near the lake (Laguna de Bay), higher flood risk
    if brgy in ["Malaban", "Casile", "De La Paz", "San Jose", "San Antonio"]:
        haz_type = "Flood"
        haz_lvl = np.random.choice(["High", "Critical"])
    else:
        haz_type = np.random.choice(["Flood", "Earthquake", "Fire"], p=[0.5, 0.3, 0.2])
        haz_lvl = np.random.choice(["Low", "Medium", "High"], p=[0.4, 0.4, 0.2])
        
    barangays_data.append({
        "Barangay": brgy,
        "HazardType": haz_type,
        "HazardLevel": haz_lvl,
        "Population": pop,
        "Latitude": round(lat, 5),
        "Longitude": round(lon, 5)
    })

df_barangays = pd.DataFrame(barangays_data)
df_barangays.to_csv("barangays.csv", index=False)


# 2. Facilities Data
facility_types = ["Evacuation Site", "School", "Command Center", "Hospital", "Health Care Center", "Fire Station"]
facilities_data = []
fac_id = 1

for brgy in barangays_list:
    # 1 to 3 facilities per barangay
    num_fac = np.random.randint(1, 4)
    brgy_row = df_barangays[df_barangays["Barangay"] == brgy].iloc[0]
    lat = brgy_row["Latitude"]
    lon = brgy_row["Longitude"]
    
    # Track if we've added an evac site to create the BI "gap" narrative
    coastal_brgys = ["Malaban", "Casile", "De La Paz", "San Jose", "San Antonio"]
    added_evac = False
    
    for _ in range(num_fac):
        fac_type = random.choice(facility_types)
        
        # BI Narrative: Force coastal areas to have Evacuation Sites, but with very small capacity to show a "Gap"
        if brgy in coastal_brgys and not added_evac:
            fac_type = "Evacuation Site"
            added_evac = True
            
        if fac_type == "Evacuation Site":
            # Realistic Philippines scenario: Capacities trail behind the massive number of affected
            cap = random.randint(800, 1800) if brgy in coastal_brgys else random.randint(300, 800)
            # BI Story: Coastal Evacuation Sites are heavily used, so their resources are often depleted
            res = random.randint(10, 45) if brgy in coastal_brgys else random.randint(40, 90)
        else:
            cap = random.randint(10, 100)
            res = random.randint(50, 100)
            
        # Prevent markers from spawning in Laguna de Bay (which is East / positive Longitude)
        lat_offset = random.uniform(-0.008, 0.008)
        # If it's a coastal barangay, only allow Western (negative) or very slight Eastern offsets
        lon_offset = random.uniform(-0.008, 0.002) if brgy in coastal_brgys else random.uniform(-0.008, 0.008)
        
        facilities_data.append({
            "FacilityID": f"F{fac_id:03d}",
            "Name": f"{brgy} {fac_type}",
            "Barangay": brgy,
            "Type": fac_type,
            "Capacity": cap,
            "Occupants": random.randint(int(cap * 0.4), int(cap * 0.9)), 
            "ResourcesAvailable": res,
            "Latitude": round(lat + lat_offset, 6),
            "Longitude": round(lon + lon_offset, 6)
        })
        fac_id += 1

df_facilities = pd.DataFrame(facilities_data)
df_facilities.to_csv("facilities.csv", index=False)


# 3. Rescue Teams Data
team_specialties = ["Water Rescue", "Medical", "Search & Rescue", "Fire Response", "General Purpose"]
teams_data = []
team_id = 1

# Not every barangay has a dedicated team, some are centralized
for i in range(15):
    brgy = np.random.choice(barangays_list)
    spec = np.random.choice(team_specialties)
    status = np.random.choice(["On Duty", "Available", "Deployed"], p=[0.3, 0.5, 0.2])
    
    brgy_lat = df_barangays[df_barangays["Barangay"] == brgy]["Latitude"].values[0]
    brgy_lon = df_barangays[df_barangays["Barangay"] == brgy]["Longitude"].values[0]
    
    teams_data.append({
        "TeamID": f"TEAM-{team_id:03d}",
        "Name": f"Biñan Rescue Squad {team_id}",
        "BaseBarangay": brgy,
        "Specialty": spec,
        "Status": status,
        "OnDuty": status == "On Duty",
        "Latitude": round(brgy_lat, 5),
        "Longitude": round(brgy_lon, 5)
    })
    team_id += 1

df_teams = pd.DataFrame(teams_data)
df_teams.to_csv("rescue_teams.csv", index=False)


# 4. Incidents Data
incidents_data = []
incident_types = ["Flood", "Medical Emergency", "Fire", "Traffic Accident", "Structural Collapse"]
severities = ["Low", "Moderate", "High", "Critical"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 5, 1)
delta = end_date - start_date

# Generate a list of all unique year-month periods between start and end date
all_months = []
curr = start_date
while curr <= end_date:
    all_months.append((curr.year, curr.month))
    curr += timedelta(days=31)
    curr = curr.replace(day=1)

for i in range(75):
    # Guarantee at least 1 incident per month to avoid unrealistic '0' gaps
    if i < len(all_months):
        y, m = all_months[i]
        import calendar
        last_day = calendar.monthrange(y, m)[1]
        random_day = random.randint(1, last_day)
        dt = datetime(y, m, random_day, random.randrange(24), random.randrange(60))
    else:
        # Realistic gradual seasonal trend (Bell Curve peaking in Aug/Sep)
        while True:
            random_days = random.randrange(delta.days)
            dt = start_date + timedelta(days=random_days, hours=random.randrange(24), minutes=random.randrange(60))
            
            # Smooth probability curve for a gradual rise and fall
            m = dt.month
            if m in [1, 2, 3, 4, 11, 12]: prob = 0.10
            elif m in [5, 10]:            prob = 0.40
            elif m in [6, 9]:             prob = 0.70
            elif m in [7, 8]:             prob = 0.95
            
            if random.random() < prob: 
                break
            
    # Determine incident type based on the season
    if dt.month in [7, 8, 9, 10]:
        # Rainy season: Massive flood focus
        inc_type = np.random.choice(incident_types, p=[0.85, 0.05, 0.02, 0.05, 0.03])
    elif dt.month in [3, 4, 5]:
        # Summer season (Philippines): Higher chance of Fire, but still keep Flood present
        inc_type = np.random.choice(incident_types, p=[0.50, 0.10, 0.25, 0.10, 0.05])
    else:
        # Normal months
        inc_type = np.random.choice(incident_types, p=[0.75, 0.10, 0.05, 0.05, 0.05])
    
    # Realistic flood placement: Heavy on coastal barangays
    coastal_brgys = ["Malaban", "De La Paz", "Casile", "San Jose", "San Antonio"]
    inland_brgys = [b for b in barangays_list if b not in coastal_brgys]
    
    if inc_type == "Flood":
        if random.random() < 0.8:
            brgy = np.random.choice(coastal_brgys)
        else:
            brgy = np.random.choice(inland_brgys)
    else:
        brgy = np.random.choice(barangays_list)
    
    # Correlate severity with type
    if inc_type == "Flood":
        if brgy in coastal_brgys:
            # Less exaggerated criticals, but still high threat
            sev = np.random.choice(severities, p=[0.10, 0.30, 0.45, 0.15])
        else:
            sev = np.random.choice(severities, p=[0.20, 0.50, 0.25, 0.05])
        # Unique affected numbers using a larger range and random addition
        affected = np.random.randint(50, 450) + random.randint(1, 49)
    elif inc_type == "Fire":
        sev = np.random.choice(severities, p=[0.2, 0.3, 0.3, 0.2])
        affected = np.random.randint(10, 80) + random.randint(1, 19)
    else:
        sev = np.random.choice(severities)
        affected = np.random.randint(1, 15) + random.randint(1, 5)
        
    brgy_lat = df_barangays[df_barangays["Barangay"] == brgy]["Latitude"].values[0]
    brgy_lon = df_barangays[df_barangays["Barangay"] == brgy]["Longitude"].values[0]
    
    # Introduce some missing values intentionally for ETL points
    if np.random.rand() < 0.02:
        affected = np.nan
    
    # Spatial Distancing: Ensure this incident doesn't overlap, but stay strictly INSIDE Biñan
    max_attempts = 50
    for attempt in range(max_attempts):
        # Tighter jitter (0.0035 = ~380m) so it doesn't spill into Cavite/Carmona/Sta Rosa
        lat_offset = random.uniform(-0.0035, 0.0035)
        # Prevent incidents from spawning in Laguna de Bay for coastal barangays
        lon_offset = random.uniform(-0.0035, 0.001) if brgy in coastal_brgys else random.uniform(-0.0035, 0.0035)
        
        new_lat = round(brgy_lat + lat_offset, 6)
        new_lon = round(brgy_lon + lon_offset, 6)
        
        # Check distance against all previously generated incidents
        too_close = False
        for inc in incidents_data:
            dist = ((inc["Latitude"] - new_lat)**2 + (inc["Longitude"] - new_lon)**2)**0.5
            if dist < 0.0012: # ~130 meters minimum distance, enough to see separate dots without spilling
                too_close = True
                break
                
        if not too_close:
            break # Found a perfectly distanced spot!

    incidents_data.append({
        "IncidentID": f"I{i+1:03d}",
        "DateTime": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "Barangay": brgy,
        "Type": inc_type,
        "Severity": sev,
        "NumAffected": affected,
        "Latitude": new_lat,
        "Longitude": new_lon
    })

df_incidents = pd.DataFrame(incidents_data)

# Sort by date
df_incidents = df_incidents.sort_values(by="DateTime")
df_incidents.to_csv("incidents.csv", index=False)

print("Data generation complete! 4 CSV files created in", os.getcwd())
