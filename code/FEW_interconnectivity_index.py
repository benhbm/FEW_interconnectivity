# Interconnectivity Magnitude Index
import os
import pandas as pd

# Configuration
scenarios = [
    "ssp1",
    "ssp2",
    "ssp5",
    "ssp1rcp19",
    "ssp1rcp26",
    "ssp2rcp45",
    "ssp5rcp34",
    "ssp5rcp60",
]

regions_selected = [
    "Africa_Eastern", "Africa_Northern", "Africa_Southern", "Africa_Western",
    "Argentina", "Australia_NZ", "Brazil", "Canada",
    "Central America and Caribbean", "Central Asia", "China", "Colombia",
    "EU-12", "EU-15", "Europe_Eastern", "European Free Trade Association",
    "Europe_Non_EU", "India", "Indonesia", "Japan", "Mexico", "Middle East",
    "Pakistan", "Russia", "South Africa", "South America_Northern",
    "South America_Southern", "South Asia", "Southeast Asia", "South Korea",
    "Taiwan", "USA",
    "World",
]

years_selected = [2015, 2050, 2100]

feedback_sectors = ["water", "electricity", "agriculture", "energy"]

flow_dir = r"..\output\flow"
output_dir = r"..\output\magnitude"
os.makedirs(output_dir, exist_ok=True)

df_flow = pd.read_excel(os.path.join(flow_dir, "FEW flow.xlsx"))

records = []
for scenario in scenarios:
    for region in regions_selected:
        for year in years_selected:
            flow = df_flow[
                (df_flow["scenario"] == scenario)
                & (df_flow["region"] == region)
                & (df_flow["Year"] == year)
                & (df_flow["sourceSector"].isin(feedback_sectors))
            ]
            if not flow.empty:
                flow_fb = flow[flow["destinationSector"].isin(feedback_sectors)]
                magnitude = flow_fb["share"].sum() / flow["share"].sum()
                records.append({
                    "scenario": scenario,
                    "region": region,
                    "Year": year,
                    "magnitude": magnitude,
                })

df_magnitude = pd.DataFrame(records, columns=["scenario", "region", "Year", "magnitude"])
df_magnitude.to_excel(os.path.join(output_dir, "FEW magnitude.xlsx"), index=False)
