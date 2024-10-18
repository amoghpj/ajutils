import pandas as pd
import sys
import numpy as np
def plate_reader_excel(path, kind="od600",startrow=33,endrow=76):
    """
    =kind= can be one of 
    1. "od600"
    2. "spectral"
    3. "kinetic"
    """
    if kind == "od600":
        df = pd.read_excel(path)
    elif kind == "kinetic":
        dfvals = pd.read_excel(path,
                               skiprows=range(startrow-2))\
                   .values[:endrow - startrow,1:]
        df = pd.DataFrame(dfvals[1:,:], columns = dfvals[0])
        try:
            df = df.melt(id_vars=["Time"], 
                         value_vars=[c for c in df.columns if c not in ["Time","T° 600"]],
                         var_name="Well",
                         value_name="OD600")
            time = pd.to_datetime(df.Time, format="%H:%M:%S")
            df = df.assign(Time_hr = (time - min(time)).dt.seconds/3600,
                           Row = [v[0] for v in df.Well.values],
                           Column = [int(v[1:]) for v in df.Well.values])
        except:
            print("WARNING: Failed to melt dataframe.")
        
    elif kind == "spectral":
        dfvals = pd.read_excel(path,
                               skiprows=range(startrow-2)).values[:endrow-startrow-1,1:]
        df = pd.DataFrame(dfvals[1:,:], columns = dfvals[0])
        wells = [c for c in df.columns if c !="Wavelength"]
        df = df.melt(id_vars="Wavelength", value_vars=wells,
                     value_name="Intensity", var_name="Well")
        df = df.assign(Row = [str(v[0]) for v in df.Well.values],
                       Col = [int(v[1:]) for v in df.Well.values])
    else:
        raise NotImplementedError
    return(df)

def qpcr_reader_excel(path):
    """
    Return three data frames: results, samples and melt curve.
    If melt curve is absent, return None.
    """
    results = pd.read_excel(path,
                            sheet_name="Results",
                            header=None)
    for i, v in  enumerate(results[0].values):
        if type(v) is not str:
            break
    results = pd.DataFrame(results.values[i+2:,:],
                           columns=results.values[i+1])
    # results = pd.read_excel(path,
    #                         sheet_name="Amplification Data",
    #                         header=None)
    samples = pd.read_excel(path,
                                  header=None,
                                  sheet_name="Sample Setup"
                                  )
    for i, v in  enumerate(samples[0].values):
        if type(v) is not str:
            break
    samples = pd.DataFrame(samples.values[i+2:,:],
                           columns = samples.values[i+1,:])
    try:
        meltcurve = pd.read_excel(path,
                                  header=None,
                                  sheet_name="Melt Curve Raw Data"
                                  )
        meltcurve = pd.DataFrame(meltcurve.values[i+2:,:], 
                             columns=meltcurve.values[i+1])
    except:
        meltcurve = None
    results["Row"] = [v[0] for v in results["Well Position"]]
    results["Column"] = [int(v[1:]) for v in results["Well Position"]]
    ## Column "Baseline End" stores the number of cycles.
    results["CT"] = results.CT.replace({"Undetermined":results["Baseline End"].max()})
    results["CT"] = results["CT"].astype(float)
    return(results, samples, meltcurve)

def process_metadata(meta, metaorder):
    meta = np.array(meta)
    columns = metaorder.split(":")
    mdf = pd.DataFrame(meta[0:,1:], 
                       index=pd.Index(meta[:,0]),
                       columns=list(range(1,25))).reset_index()\
                       .rename({"index":"Row"}, axis="columns")
    mdf = mdf.melt(id_vars="Row",value_vars=mdf.columns,
                   value_name=metaorder,
                   var_name="Column")
    for colid, col in enumerate(columns):
        mdf[col] = mdf[metaorder].str.split(":",expand=True)[colid]
    return(mdf)
