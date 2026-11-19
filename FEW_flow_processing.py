# Physical intersectoral flow-accounting framework
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
]

years_selected = [2015, 2050, 2100]

data_dir = r"..\data"
output_dir = r"..\output\flow"
os.makedirs(output_dir, exist_ok=True)


# Sector mappings
WATER_MAP = {
    **{s: "agriculture" for s in [
        "Beef", "Corn", "Dairy", "FiberCrop", "FodderGrass", "FodderHerb",
        "Fruits", "Legumes", "MiscCrop", "NutsSeeds", "OilCrop", "OilPalm",
        "OtherGrain", "Pork", "Poultry", "Rice", "RootTuber", "SheepGoat",
        "Soybean", "SugarCrop", "Vegetables", "Wheat", "biomass",
    ]},
    **{s: "energy" for s in [
        "nuclearFuelGenII", "nuclearFuelGenIII", "regional coal", "regional oil",
        "H2 central production", "H2 industrial", "H2 wholesale dispensing",
    ]},
    **{s: "electricity" for s in [
        "elec_biomass (IGCC CCS)", "elec_biomass (conv CCS)",
        "elec_coal (IGCC CCS)", "elec_coal (conv pul CCS)",
        "elec_gas (CC CCS)", "elec_refined liquids (CC CCS)", "electricity",
    ]},
    **{s: "industry" for s in ["food processing", "other industry", "paper"]},
    "municipal water": "municipal",
}

ELECTRICITY_MAP = {
    "agricultural energy use": "agriculture",
    **{s: "energy" for s in [
        "mining energy use", "H2 central production", "H2 industrial",
        "H2 liquid truck", "H2 pipeline", "refining", "H2 wholesale dispensing",
    ]},
    **{s: "water" for s in [
        "municipal wastewater treatment", "municipal water abstraction",
        "municipal water distribution", "municipal water treatment",
        "desalinated water", "industrial wastewater treatment",
        "industrial water abstraction", "industrial water treatment",
        "irrigation water abstraction",
    ]},
    **{s: "industry" for s in [
        "aluminum", "cement", "chemical energy use", "construction energy use",
        "food processing", "iron and steel", "other industrial energy use",
        "paper", "process heat food processing", "process heat paper",
    ]},
    **{s: "municipal" for s in [
        "comm cooling", "comm heating", "comm others",
        *[f"resid cooling modern_d{i}" for i in range(1, 11)],
        *[f"resid heating modern_d{i}" for i in range(1, 11)],
        *[f"resid others modern_d{i}" for i in range(1, 11)],
        "trn_aviation_intl", "trn_freight", "trn_freight_road", "trn_pass",
        "trn_pass_road", "trn_pass_road_LDV", "trn_pass_road_LDV_4W",
        "trn_shipping_intl",
    ]},
}

ENERGY_MAP = {
    "agricultural energy use": "agriculture",
    **{s: "water" for s in [
        "desalinated water", "industrial wastewater treatment",
        "industrial water abstraction", "industrial water treatment",
        "irrigation water abstraction", "municipal wastewater treatment",
        "municipal water abstraction", "municipal water distribution",
        "municipal water treatment",
    ]},
    **{s: "industry" for s in [
        "alumina", "aluminum", "ammonia", "cement", "chemical energy use",
        "chemical feedstocks", "construction energy use", "construction feedstocks",
        "food processing", "iron and steel", "mining energy use",
        "other industrial energy use", "other industrial feedstocks", "paper",
        "process heat cement", "process heat food processing",
        "process heat paper", "waste biomass for paper",
    ]},
    **{s: "municipal" for s in [
        "comm cooling", "comm heating", "comm others",
        *[f"resid cooling modern_d{i}" for i in range(1, 11)],
        *[f"resid heating TradBio_d{i}" for i in range(1, 11)],
        *[f"resid heating coal_d{i}" for i in range(1, 11)],
        *[f"resid heating modern_d{i}" for i in range(1, 11)],
        *[f"resid others TradBio_d{i}" for i in range(1, 11)],
        *[f"resid others coal_d{i}" for i in range(1, 11)],
        *[f"resid others modern_d{i}" for i in range(1, 11)],
        "trn_aviation_intl", "trn_freight", "trn_freight_road", "trn_pass",
        "trn_pass_road", "trn_pass_road_LDV", "trn_pass_road_LDV_4W",
        "trn_shipping_intl",
    ]},
}

CROP_MAP = {
    "regional corn for ethanol": "energy",
    "regional biomassOil": "energy",
    "regional sugar for ethanol": "energy",
    "NonFoodDemand_Crops": "industry",
    "FoodDemand_Staples": "municipal",
    "FoodDemand_NonStaples": "municipal",
}

MEAT_MAP = {
    "NonFoodDemand_Meat": "industry",
    "FoodDemand_NonStaples": "municipal",
}


def _aggregate_flows(df, source_sector, destination_sectors):
    results = []
    for dest in destination_sectors:
        sub = df[df["destinationSector"] == dest]
        agg = sub.groupby(["region", "Year"])["value"].sum().reset_index()
        agg["sourceSector"] = source_sector
        agg["destinationSector"] = dest
        results.append(agg)
    return results


# Water (km^3)
def process_water(scenario):
    df = pd.read_excel(os.path.join(data_dir, f"water withdrawals by sector_{scenario}.xlsx"))
    df["destinationSector"] = df["sector"].map(WATER_MAP)
    df = df[df["region"].isin(regions_selected) & df["Year"].isin(years_selected)]
    return _aggregate_flows(df, "water", ["agriculture", "energy", "electricity", "industry", "municipal"])


# Electricity (EJ)
def process_electricity(scenario):
    df = pd.read_excel(os.path.join(data_dir, f"elec consumption by demand sector_{scenario}.xlsx"))
    df["destinationSector"] = df["sector"].map(ELECTRICITY_MAP)
    df = df[df["region"].isin(regions_selected) & df["Year"].isin(years_selected)]
    return _aggregate_flows(df, "electricity", ["agriculture", "energy", "water", "industry", "municipal"])


# Energy (EJ)
def process_energy(scenario):
    df_final = pd.read_excel(os.path.join(data_dir, f"final energy consumption by sector and fuel_{scenario}.xlsx"))
    df_final["destinationSector"] = df_final["sector"].map(ENERGY_MAP)
    df_final = df_final[df_final["input"] != "electricity"]
    df_final = df_final[df_final["region"].isin(regions_selected) & df_final["Year"].isin(years_selected)]
    flows = _aggregate_flows(df_final, "energy", ["agriculture", "water", "industry", "municipal"])

    df_elec = pd.read_excel(os.path.join(data_dir, f"elec energy input by subsector_{scenario}.xlsx"))
    df_elec = df_elec[df_elec["subsector"] != "biomass"]
    df_elec = df_elec[df_elec["region"].isin(regions_selected) & df_elec["Year"].isin(years_selected)]
    agg_elec = df_elec.groupby(["region", "Year"])["value"].sum().reset_index()
    agg_elec["sourceSector"] = "energy"
    agg_elec["destinationSector"] = "electricity"

    return [flows[0], agg_elec, flows[1], flows[2], flows[3]]


# Agriculture (Mt)
def process_agriculture(scenario):
    df_crop = pd.read_excel(os.path.join(data_dir, f"demand balances by crop commodity_{scenario}.xlsx"))
    df_crop["destinationSector"] = df_crop["sector"].map(CROP_MAP)
    df_crop = df_crop[df_crop["region"].isin(regions_selected) & df_crop["Year"].isin(years_selected)]

    df_meat = pd.read_excel(os.path.join(data_dir, f"demand balances by meat and dairy commodity_{scenario}.xlsx"))
    df_meat["destinationSector"] = df_meat["sector"].map(MEAT_MAP)
    df_meat = df_meat[df_meat["region"].isin(regions_selected) & df_meat["Year"].isin(years_selected)]

    df_comm = pd.concat(
        [
            df_crop[["scenario", "region", "Year", "value", "destinationSector"]],
            df_meat[["scenario", "region", "Year", "value", "destinationSector"]],
        ],
        ignore_index=True,
    )

    df_param = pd.read_excel(r"biomass parameter.xlsx")
    df_res = pd.read_excel(os.path.join(data_dir, f"residue biomass production_{scenario}.xlsx"))
    df_res = df_res.merge(df_param[["crop", "mass-to-energy", "water-content"]], left_on="sector", right_on="crop", how="left")
    df_res["mass"] = df_res["value"] / (df_res["mass-to-energy"] * (1 - df_res["water-content"]))
    df_res_sum = df_res.groupby(["Units", "scenario", "region", "output", "Year"])["mass"].sum().reset_index()
    df_res_sum["Units"] = "Mt"
    df_res_sum.rename(columns={"mass": "value"}, inplace=True)

    df_pg = pd.read_excel(os.path.join(data_dir, f"purpose-grown biomass production_{scenario}.xlsx"))
    df_pg["value"] = df_pg["value"] / 0.018
    df_pg["Units"] = "Mt"
    df_pg = df_pg[df_pg["region"].isin(regions_selected) & df_pg["Year"].isin(years_selected)]

    df_bio_mass = pd.merge(
        df_res_sum[["Units", "scenario", "region", "Year", "value"]],
        df_pg[["Units", "scenario", "region", "Year", "value"]],
        on=["Units", "scenario", "region", "Year"],
        how="outer",
        suffixes=("_res", "_pg"),
    ).fillna(0)
    df_bio_mass["total_mass"] = df_bio_mass["value_res"] + df_bio_mass["value_pg"]

    df_bio_tot = pd.read_excel(os.path.join(data_dir, f"regional biomass consumption_{scenario}.xlsx"))
    df_bio_el = pd.read_excel(os.path.join(data_dir, f"elec energy input by subsector_{scenario}.xlsx"))
    df_bio_el = df_bio_el[df_bio_el["subsector"] == "biomass"]

    df_alloc = pd.merge(
        df_bio_tot[["region", "Year", "value"]],
        df_bio_el[["region", "Year", "value"]],
        on=["region", "Year"],
        how="outer",
        suffixes=("_tot", "_el"),
    )
    df_alloc = df_alloc[df_alloc["region"].isin(regions_selected) & df_alloc["Year"].isin(years_selected)]
    df_alloc["electricity"] = df_alloc["value_el"] / df_alloc["value_tot"]
    df_alloc["energy"] = 1 - df_alloc["electricity"]

    df_bio = pd.merge(df_bio_mass, df_alloc[["region", "Year", "electricity", "energy"]], on=["region", "Year"], how="inner")
    df_bio["electricity"] = df_bio["total_mass"] * df_bio["electricity"]
    df_bio["energy"] = df_bio["total_mass"] * df_bio["energy"]

    df_bio_panel = pd.melt(
        df_bio,
        id_vars=["Units", "scenario", "region", "Year"],
        value_vars=["electricity", "energy"],
        var_name="destinationSector",
        value_name="value",
    )[["scenario", "region", "Year", "value", "destinationSector"]]

    df_ag = pd.concat([df_comm, df_bio_panel], axis=0, ignore_index=True)
    return _aggregate_flows(df_ag, "agriculture", ["electricity", "energy", "industry", "municipal"])


# Flow matrix construction
output_columns = ["scenario", "region", "Year", "sourceSector", "destinationSector", "value", "share"]
all_scenario_flows = []

for scenario in scenarios:
    ag_flows = process_agriculture(scenario)
    el_flows = process_electricity(scenario)
    en_flows = process_energy(scenario)
    wt_flows = process_water(scenario)

    all_flows = ag_flows + el_flows + en_flows + wt_flows

    # Regional flow matrix
    flow_region = pd.concat(all_flows, ignore_index=True)
    flow_region["total"] = flow_region.groupby(["region", "Year", "sourceSector"])["value"].transform("sum")
    flow_region["share"] = flow_region["value"] / flow_region["total"]
    flow_region["scenario"] = scenario
    flow_region = flow_region[output_columns]

    # Global flow matrix
    flow_world = pd.concat(all_flows, ignore_index=True)
    flow_world = flow_world.groupby(["Year", "sourceSector", "destinationSector"])["value"].sum().reset_index()
    flow_world["total"] = flow_world.groupby(["Year", "sourceSector"])["value"].transform("sum")
    flow_world["share"] = flow_world["value"] / flow_world["total"]
    flow_world["region"] = "World"
    flow_world["scenario"] = scenario
    flow_world = flow_world[output_columns]

    all_scenario_flows.extend([flow_region, flow_world])

flow_all = pd.concat(all_scenario_flows, ignore_index=True)
flow_all.to_excel(os.path.join(output_dir, "FEW flow.xlsx"), index=False)
