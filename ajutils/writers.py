import pandas as pd
from tqdm import tqdm
from datetime import datetime
import json
import sys


def process_for_viability_server(df ,outname="out.json", grouping=[]):
    """
    Format an experiment for upload to the viability interface
    Arguments:
      - raw - pd.Dataframe of CT values
      - rawamp - pd.Dataframe of Delta Rn  values
      - processed - pd.DataFrame of 
    """

    out = []
    _groups = [ "Organism",
                "conops",
                "treatment",
                "day",
               ]
    _groups.extend(grouping)
    _experiment_fields = [
        ## Global
        "experiment_id",
        "repid",
        "dilution",
        "replicate",
        "sampletype",
        "sp_id",
        "initial_viability",
        "user", 
        "growth",
        "ProbeID",
        ## Optional if processeing assessment data
]
    _all_fields = list(_experiment_fields)
    _all_fields.extend([
        ## CT data
        "CT",
        ## Amplification data
        "Delta Rn",
        ## From processed data
        "is_valid_ct",
        "d1initial",
        "d2initial",
        "notes"])
    _all_fields.extend(grouping)



    ##########
    ## Normalize organism name column
    possible_organism_columns = ["Sp","species","Species","organism"]
    for col in possible_organism_columns:
        if col in df.columns:
            df = df.rename({col:"Organism"},
                           axis="columns")
    ##########
    ### Create unique species IDs automatically, these 
    ### are used across this experiment
    indexeddf = df[["Organism"]]\
        .drop_duplicates()\
        .reset_index(drop=True)\
        .reset_index()\
        .rename({"index":"Idx"},
                axis="columns")
    df = df.merge(indexeddf, on="Organism")
    df = df.assign(sp_id = df.experiment_id\
                   .str.cat([df.Idx.astype(str),\
                             df.day.astype(str)], 
                            sep="_"))

    for dilcols in ["d1initial","d2initial"]:
        if dilcols not in df.columns:
            df[dilcols] = None    

    for col in _all_fields:
        if col not in df.columns:
            print(f"LOG: {col} is missing")
            df[col] = ""
    ### At this point, we need to start doing grouping on columns.
    ### On each group, we extract some experiment specific parameters, then drill down to get the raw data
    #filterdf = df[_groups].drop_duplicates()
    def extract_raw(gdf):
        return({"is_valid_ct":gdf.is_valid_ct.values[0],
                "replicate":int(gdf.replicate.values[0]),
                "repid":int(gdf.repid.values[0]),
                "dilution":int(gdf.dilution.values[0]),
                "CT":float(gdf.CT.values[0]),
                "Delta Rn": gdf["Delta Rn"].to_list(),
                "notes":gdf["notes"].values[0]
                })

    def extract_specs(gdf, fulldf):
        """
        Single grouped dataframe, as well as the full dataframe to access the raw data.
        """
        ## Initialize
        _COI = ["repid","dilution","replicate"]
        expdict = dict()
        raw_columns = ["is_valid_ct","replicate", "repid", "dilution", "CT", "Delta Rn", "notes"]
        row = gdf[[c for c in gdf.columns if c not in raw_columns]]\
            .drop_duplicates()\
            .reset_index(drop=True)\
            .iloc[0]

        rowdf = pd.DataFrame({k:[v] for k, v in row.items()})

        ## Assign
        expdict["day"] =  int(row.day)
        expdict["organism"] =  str(row.Organism)
        expdict["sampletype"] =  str(row.sampletype)
        expdict["experiment_id"] = str(row.experiment_id)
        expdict["sp_id"] = str(row.sp_id)
        expdict["initial_viability_id"] = str(row.initial_viability)
        expdict["user"] = str(row.user)
        expdict["viability_estimate"] = float(row.growth)
        expdict["conops"] = str(row["conops"])
        expdict["treatment"] = str(row["treatment"])
        expdict["raw_data"] = []
        expdict["d1initial"] = row.d1initial
        expdict["d2initial"] = row.d2initial
        expdict["probe_id"] = str(row.ProbeID)
        expdict["date"] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
        ### Next, for each dilution, replicate and repid store raw CT, amp curve, 
        ### and whether it is a valid CT.
        rawdf = fulldf.merge(rowdf, 
                         on = list(set(rowdf.columns).intersection(set(fulldf.columns))),)

        expdict["raw_data"] = list(rawdf.groupby(_COI)\
                                   .apply(extract_raw).reset_index(drop=True).values)
        return(expdict)

    out = list(df.groupby(_groups)\
                .apply(extract_specs, 
                       fulldf = df)\
                .reset_index(drop=True).values)

    out = {"experiments":out}
    with open(outname, "w") as outfile:
        json.dump(out, outfile)

def normalize_columns(df):
    if "Dilution"  in df.columns:
        df = df.rename({"Dilution":"dilution"}, axis="columns")
    return df
