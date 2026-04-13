#!/usr/bin/env python3
"""
Generate realistic sample data for frontend development.
Creates mock FEC disbursement data with vendor locations
in swing-state cities, party splits, and spend distributions.
"""

import json
import random
import math
from pathlib import Path

random.seed(42)

EXPORTS_DIR = Path(__file__).parent.parent / "data" / "exports"
STATIC_DIR = Path(__file__).parent.parent / "web" / "static" / "data"

# Vendor clusters in key cities — (center_lat, center_lng, radius_degrees)
CITY_CLUSTERS = {
    "Philadelphia": (39.9526, -75.1652, 0.015),
    "Atlanta": (33.7490, -84.3880, 0.012),
    "Phoenix": (33.4484, -112.0740, 0.018),
    "Detroit": (42.3314, -83.0458, 0.010),
    "Las Vegas": (36.1699, -115.1398, 0.014),
    "Milwaukee": (43.0389, -87.9065, 0.008),
    "Miami": (25.7617, -80.1918, 0.012),
    "Washington DC": (38.9072, -77.0369, 0.020),
    "New York": (40.7128, -74.0060, 0.010),
    "Chicago": (41.8781, -87.6298, 0.008),
    "Los Angeles": (34.0522, -118.2437, 0.015),
    "Houston": (29.7604, -95.3698, 0.010),
    "Pittsburgh": (40.4406, -79.9959, 0.008),
    "Tucson": (32.2226, -110.9747, 0.010),
    "Raleigh": (35.7796, -78.6382, 0.010),
}

# Realistic political vendor names
VENDOR_TEMPLATES = {
    "MEDIA_BUYING": [
        "GMMB Inc", "Waterfront Strategies", "Canal Partners Media",
        "Bully Pulpit Interactive", "Precision Strategies",
        "Rising Tide Interactive", "Trilogy Interactive",
        "Screen Strategies Media", "Buying Time Media",
        "Media Strategies & Research", "Convergence Media",
        "Smart Media Group", "Red Eagle Media Group",
        "Targeted Victory", "Mentzer Media Services",
        "Nation Media LLC", "American Media & Advocacy Group",
        "Strategic Media Placement", "National Media Research",
    ],
    "DIRECT_MAIL": [
        "Mission Control Inc", "Chapman Cubine & Hussey",
        "Optimus Consulting", "Arena Communications",
        "Response Dynamics", "HSP Direct",
        "Direct Mail Systems", "Persuasion Partners",
        "Blue State Digital", "Revolution Messaging",
        "Mail Haus LLC", "Pacific Campaign House",
        "Patriot Signaling LLC", "Red Curve Solutions",
    ],
    "CONSULTING": [
        "SKDKnickerbocker", "Benenson Strategy Group",
        "GBAO Strategies", "Global Strategy Group",
        "ALG Research", "Hart Research Associates",
        "Anzalone Liszt Grove Research", "Lake Research Partners",
        "Public Opinion Strategies", "The Tarrance Group",
        "Echelon Insights", "North Star Opinion Research",
        "WPA Intelligence", "Fabrizio Ward & Associates",
    ],
    "DATA_ANALYTICS": [
        "Civis Analytics", "HaystaqDNA", "TargetSmart",
        "L2 Political", "Aristotle International",
        "i360 LLC", "Data Trust", "Deep Root Analytics",
        "BlueLabs Analytics", "Catalist LLC",
    ],
    "FIELD_OPERATIONS": [
        "Field First Inc", "Grassroots Campaigns",
        "Movement Labs", "Community Change Action",
        "Fieldworks LLC", "Ground Game Strategies",
        "Mobilize Communities Inc", "Rally Forge LLC",
    ],
    "DIGITAL": [
        "Authentic Campaigns", "Middle Seat Consulting",
        "Mothership Strategies", "Bask Digital Media",
        "Push Digital Group", "Flex Point Media",
        "Grow Progress", "Accelerate Action",
    ],
    "LEGAL": [
        "Perkins Coie LLP", "Elias Law Group",
        "Jones Day", "Holtzman Vogel Baran",
        "Wiley Rein LLP", "Covington & Burling",
    ],
    "PRINTING": [
        "Cramer-Krasselt", "LSB Print Solutions",
        "Merrill Press", "Allegra Network",
        "Colonial Press International", "Robindale Printing",
    ],
    "EVENT_PRODUCTION": [
        "TBA Global Events", "Hargrove Engineers",
        "PSAV Presentation Services", "Event Strategies Inc",
    ],
    "TV_STATIONS": [
        "WPVI-TV Philadelphia", "WCAU-TV Philadelphia",
        "WSB-TV Atlanta", "WXIA-TV Atlanta",
        "KNXV-TV Phoenix", "KPHO-TV Phoenix",
        "WDIV-TV Detroit", "WXYZ-TV Detroit",
        "KLAS-TV Las Vegas", "KVVU-TV Las Vegas",
        "WTMJ-TV Milwaukee", "WISN-TV Milwaukee",
        "WSVN-TV Miami", "WPLG-TV Miami",
    ],
}

# State-level spending data (based on real 2024 competitiveness)
STATE_SPEND = {
    "PA": {"dem_spend": 245_000_000, "rep_spend": 231_000_000, "vendor_count": 89},
    "MI": {"dem_spend": 178_000_000, "rep_spend": 165_000_000, "vendor_count": 62},
    "WI": {"dem_spend": 142_000_000, "rep_spend": 138_000_000, "vendor_count": 48},
    "AZ": {"dem_spend": 168_000_000, "rep_spend": 172_000_000, "vendor_count": 55},
    "NV": {"dem_spend": 118_000_000, "rep_spend": 112_000_000, "vendor_count": 38},
    "GA": {"dem_spend": 195_000_000, "rep_spend": 188_000_000, "vendor_count": 71},
    "NC": {"dem_spend": 98_000_000, "rep_spend": 105_000_000, "vendor_count": 42},
    "FL": {"dem_spend": 85_000_000, "rep_spend": 142_000_000, "vendor_count": 58},
    "OH": {"dem_spend": 62_000_000, "rep_spend": 78_000_000, "vendor_count": 35},
    "TX": {"dem_spend": 55_000_000, "rep_spend": 88_000_000, "vendor_count": 45},
    "CA": {"dem_spend": 120_000_000, "rep_spend": 45_000_000, "vendor_count": 52},
    "NY": {"dem_spend": 95_000_000, "rep_spend": 42_000_000, "vendor_count": 48},
    "IL": {"dem_spend": 38_000_000, "rep_spend": 22_000_000, "vendor_count": 25},
    "VA": {"dem_spend": 42_000_000, "rep_spend": 35_000_000, "vendor_count": 28},
    "MN": {"dem_spend": 35_000_000, "rep_spend": 32_000_000, "vendor_count": 22},
    "CO": {"dem_spend": 28_000_000, "rep_spend": 22_000_000, "vendor_count": 18},
    "NH": {"dem_spend": 22_000_000, "rep_spend": 20_000_000, "vendor_count": 15},
    "ME": {"dem_spend": 12_000_000, "rep_spend": 10_000_000, "vendor_count": 10},
    "NE": {"dem_spend": 8_000_000, "rep_spend": 15_000_000, "vendor_count": 8},
    "MT": {"dem_spend": 18_000_000, "rep_spend": 22_000_000, "vendor_count": 12},
    "DC": {"dem_spend": 280_000_000, "rep_spend": 185_000_000, "vendor_count": 120},
}

# Add remaining states with lower spending
ALL_STATES = [
    "AL", "AK", "AR", "CT", "DE", "HI", "ID", "IN", "IA", "KS",
    "KY", "LA", "MD", "MA", "MS", "MO", "NJ", "NM", "ND", "OK",
    "OR", "RI", "SC", "SD", "TN", "UT", "VT", "WA", "WV", "WY",
]
for st in ALL_STATES:
    if st not in STATE_SPEND:
        dem = random.randint(2_000_000, 25_000_000)
        rep = random.randint(2_000_000, 25_000_000)
        STATE_SPEND[st] = {
            "dem_spend": dem,
            "rep_spend": rep,
            "vendor_count": random.randint(5, 20),
        }

# Add total_spend to each state
for st in STATE_SPEND:
    STATE_SPEND[st]["total_spend"] = (
        STATE_SPEND[st]["dem_spend"] + STATE_SPEND[st]["rep_spend"]
    )


def jitter(center, radius):
    """Random point within radius of center using polar coordinates."""
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.random())
    return center[0] + r * math.cos(angle), center[1] + r * math.sin(angle)


def power_law_spend(n, total, exponent=1.8):
    """Generate power-law distributed spend amounts."""
    raw = [(i + 1) ** (-exponent) for i in range(n)]
    total_raw = sum(raw)
    return [int(x / total_raw * total) for x in raw]


def generate_vendors():
    """Generate vendor features with realistic clustering and spend distributions."""
    features = []
    vendor_id = 0

    for city, (lat, lng, radius) in CITY_CLUSTERS.items():
        # Determine how many vendors in this city (weighted by city importance)
        if city in ("Washington DC", "Philadelphia", "Atlanta"):
            n_vendors = random.randint(35, 55)
        elif city in ("Phoenix", "Detroit", "Miami", "Las Vegas"):
            n_vendors = random.randint(18, 30)
        else:
            n_vendors = random.randint(8, 18)

        # Power-law spend for this city's vendors
        city_total = random.randint(20_000_000, 180_000_000)
        spends = power_law_spend(n_vendors, city_total)

        for i in range(n_vendors):
            vendor_id += 1
            vlat, vlng = jitter((lat, lng), radius)

            # Pick a category and vendor name
            category = random.choice(list(VENDOR_TEMPLATES.keys()))
            names = VENDOR_TEMPLATES[category]
            name = random.choice(names)
            # Add city suffix for uniqueness in some cases
            if random.random() < 0.3:
                name = f"{name} - {city}"

            # Party affiliation — media/consulting lean mixed, field ops lean DEM
            if category in ("FIELD_OPERATIONS", "DATA_ANALYTICS"):
                party = "DEM" if random.random() < 0.65 else "REP"
            elif category in ("TV_STATIONS", "PRINTING"):
                party = random.choice(["DEM", "REP"])
            else:
                party = "DEM" if random.random() < 0.52 else "REP"

            total = spends[i] if i < len(spends) else random.randint(10_000, 500_000)
            dem_spend = total if party == "DEM" else int(total * random.uniform(0.05, 0.25))
            rep_spend = total if party == "REP" else int(total * random.uniform(0.05, 0.25))

            # Cycles — older firms appear more often
            possible_cycles = [2016, 2018, 2020, 2022, 2024]
            if total > 2_000_000:
                cycles = possible_cycles  # big vendors are always repeat players
            elif total > 500_000:
                cycles = random.sample(possible_cycles, k=random.randint(2, 4))
            else:
                cycles = [2024] if random.random() < 0.6 else [2022, 2024]
            cycles.sort()

            state_map = {
                "Philadelphia": "PA", "Atlanta": "GA", "Phoenix": "AZ",
                "Detroit": "MI", "Las Vegas": "NV", "Milwaukee": "WI",
                "Miami": "FL", "Washington DC": "DC", "New York": "NY",
                "Chicago": "IL", "Los Angeles": "CA", "Houston": "TX",
                "Pittsburgh": "PA", "Tucson": "AZ", "Raleigh": "NC",
            }

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(vlng, 6), round(vlat, 6)]
                },
                "properties": {
                    "vendor_id": f"V{vendor_id:04d}",
                    "canonical_name": name,
                    "total_spend": total,
                    "dem_spend": dem_spend,
                    "rep_spend": rep_spend,
                    "dominant_party": party,
                    "cycles": cycles,
                    "category": category,
                    "city": city,
                    "state": state_map.get(city, "DC")
                }
            })

    return features


def generate_top_vendors(features):
    """Extract and rank top vendors by spend."""
    sorted_vendors = sorted(
        features, key=lambda f: f["properties"]["total_spend"], reverse=True
    )
    top = []
    for f in sorted_vendors[:50]:
        p = f["properties"]
        total = p["total_spend"]
        top.append({
            "vendor_id": p["vendor_id"],
            "canonical_name": p["canonical_name"],
            "total_spend": total,
            "dem_pct": round(p["dem_spend"] / max(total, 1) * 100, 1),
            "rep_pct": round(p["rep_spend"] / max(total, 1) * 100, 1),
            "cycles": p["cycles"],
            "category": p["category"],
            "city": p["city"],
            "state": p["state"],
        })
    return top


def generate_vendor_cycles(features):
    """Generate cycle-over-cycle spend data for repeat vendors."""
    cycles_data = []
    repeat_vendors = [
        f for f in features if len(f["properties"]["cycles"]) >= 3
    ]
    repeat_vendors.sort(key=lambda f: f["properties"]["total_spend"], reverse=True)

    for f in repeat_vendors[:30]:
        p = f["properties"]
        base = p["total_spend"]
        cycle_spends = {}
        for cycle in p["cycles"]:
            # Simulate growth over cycles
            factor = 1.0 + (cycle - 2016) * 0.15 + random.uniform(-0.2, 0.2)
            cycle_spends[str(cycle)] = int(base * factor / len(p["cycles"]))
        cycles_data.append({
            "vendor_id": p["vendor_id"],
            "canonical_name": p["canonical_name"],
            "dominant_party": p["dominant_party"],
            "category": p["category"],
            "cycles": cycle_spends,
        })
    return cycles_data


def generate_philadelphia_vendors(features):
    """Filter vendors to Philadelphia for city deep-dive."""
    philly = [
        f for f in features if f["properties"]["city"] == "Philadelphia"
    ]
    return {"type": "FeatureCollection", "features": philly}


def main():
    print("Generating sample data...")

    features = generate_vendors()
    print(f"  Generated {len(features)} vendor locations")

    # Full vendor map
    vendors_geojson = {"type": "FeatureCollection", "features": features}

    # Top vendors
    top_vendors = generate_top_vendors(features)
    print(f"  Generated top {len(top_vendors)} vendors")

    # Cycle data
    vendor_cycles = generate_vendor_cycles(features)
    print(f"  Generated cycle data for {len(vendor_cycles)} repeat vendors")

    # Philadelphia deep-dive
    philly = generate_philadelphia_vendors(features)
    print(f"  Generated {len(philly['features'])} Philadelphia vendors")

    # Write to both exports/sample and static/data
    for out_dir in [EXPORTS_DIR / "sample", STATIC_DIR]:
        out_dir.mkdir(parents=True, exist_ok=True)

        with open(out_dir / "vendors_map.geojson", "w") as f:
            json.dump(vendors_geojson, f, separators=(",", ":"))

        with open(out_dir / "state_spend.json", "w") as f:
            json.dump(STATE_SPEND, f, indent=2)

        with open(out_dir / "top_vendors.json", "w") as f:
            json.dump(top_vendors, f, indent=2)

        with open(out_dir / "vendor_cycles.json", "w") as f:
            json.dump(vendor_cycles, f, indent=2)

        with open(out_dir / "philadelphia_vendors.geojson", "w") as f:
            json.dump(philly, f, separators=(",", ":"))

    print(f"\nSample data written to:")
    print(f"  {EXPORTS_DIR / 'sample'}")
    print(f"  {STATIC_DIR}")
    print("Done!")


if __name__ == "__main__":
    main()
