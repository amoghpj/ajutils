import pandas as pd
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from itertools import product
from .colors import colors
import typing
searchpath = '/Users/amogh/projects/harvard/analysis/2025-06-17-aj02-cnn-qpcr-noise-classification/annotator/'
sys.path.insert(0, searchpath)
searchpath = '/Users/amogh/projects/harvard/analysis/2025-06-17-aj02-cnn-qpcr-noise-classification/annotator/model/'
import cnn_definition
transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5 ), (0.5 ))])
net = cnn_definition.Net()
checkpoint = torch.load(searchpath  + 'qpcr_classifier.pth', #'20250625v2-
                        map_location='cpu')
net.load_state_dict(checkpoint)
net.eval() # Set the model to evaluation mode

wellmapper384 = pd.DataFrame([{"Row":r,
                            "Column":c,
                            "well_number":i+1}
                           for i, (c, r) in 
                           enumerate(product(list(range(1,25)),
                                             ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"]
                                             ))])

wellmapper96 = pd.DataFrame([{"Row":r,
                            "Column":c,
                            "well_number":i+1}
                           for i, (c, r) in 
                           enumerate(product(list(range(1,13)),["A","B","C","D","E","F","G","H"]
                                             ))])

def makeimage(well):
    Img = np.zeros((100))
    Img[:45] = well["Delta Rn"].values
    Img[50:95] = well["Rn"].values
    Img[Img<=0] = 1
    Img = np.log10(Img)
    return(transform(Img.reshape((10,10)).astype(np.float32)).unsqueeze(0) )

def classify(gdf):
    with torch.no_grad():
        X = makeimage(gdf)
        pred = net(X)
        prediction = pred.argmax(1)
        return(gdf.assign(prediction = prediction.item())[["prediction"]].drop_duplicates())


def platereader_process_magellan(path, kind, wellplate):
    """
    Parameters
    ----------
    path : str
        Path to asc file
    kind : str
    wellplate : int
    
    Returns
    -------
    df : pandas DataFrame
        DataFrame reshaped to have the following columns:
        1. Row
        2. Column
        3. Reading
    """
    dat = pd.read_csv(path,header=None, sep="\t")
    if int(wellplate) == 384:
        df = pd.DataFrame(dat.values[1:385,:2], columns=dat.values[0,:2])
    elif int(wellplate) == 96:
        df = pd.DataFrame(dat.values[1:97,:2], columns=dat.values[0,:2])
    df = df.assign(Row = [v[0] for v in df["Well positions"]],
                   Column = [int(v[1:]) for v in df["Well positions"]],
                   OD600 = [float(v) for v in df["Raw data"]])
    return(df)

def platereader_process_infinity(path, kind, wellplate):
    """
    Parameters
    ----------
    path : str
        Path to excel file
    kind : str
    wellplate : int
    
    Returns
    -------
    df : pandas DataFrame
        DataFrame reshaped to have the following columns:
        1. Row
        2. Column
        3. Reading
    """
    dat = pd.read_excel(path, header=None)
    
    startrow = [i for i, v in enumerate(dat.values[:,0]) if v == "<>"][0] 
    startcol = 0
    if wellplate == 96:
        endrow = startrow + 8
        endcol = startcol + 12
    elif wellplate == 384:
        endrow = startrow + 17
        endcol = startcol + 25
    else:
        raise NotImplementedError
    datvals = dat.values[startrow:endrow, startcol:endcol]

    df = pd.DataFrame(datvals[1:,1:],
                      columns=datvals[0,1:],
                      index=pd.Index(datvals[1:,0]))\
           .reset_index()\
           .rename({"index":"Row"}, axis="columns")
    df = df.melt(id_vars="Row",
                 value_vars=df.columns,
                 var_name="Column",
                 value_name="OD_reading")
    return(df)

def platereader(path, 
                kind="od600",
                startrow=33,
                endrow=76,
                wellplate=96,
                instrument="infinitymplex"):
    """
    Attributes
    ----------
    path : str
        Path to excel file
    kind : str
        valid values are 
        1. "od600"
        2. "spectral"
        3. "kinetic"
    instrument : str
        Can be one of "inifinitymplex" or "biotek"
        TODO needs abstraction
    wellplate : int
        Either 96 or 384.
    """
    if instrument == "infinitymplex":
        df = platereader_process_infinity(path, kind, wellplate)
    if instrument == "magellan":
        df = platereader_process_magellan(path, kind, wellplate)
    elif instrument == "biotek":
        if kind == "od600":
            if wellplate == 96:
                df = pd.read_excel(path, skiprows=range(25), index_col=1)[[i for i in range(1,13)]]\
                       .reset_index()\
                       .rename({"index":"Row"}, axis="columns")
                df = df.melt(id_vars="Row",
                             value_vars=list(range(1,13)), 
                             var_name="Column", value_name="OD600")
            elif wellplate == 384:
                df = pd.read_excel(path, skiprows=range(24), index_col=1)[[i for i in range(1,25)]]\
                       .reset_index()\
                       .rename({"index":"Row"}, axis="columns")
                df = df.melt(id_vars="Row",
                             value_vars=list(range(1,25)), 
                             var_name="Column", value_name="OD600")
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

def fixup_ct(ctarr, maxval):
    collect = []
    for v in ctarr:
        if (str(v).lower() == "undetermined"):
            collect.append(float(maxval))
        else:
            collect.append(float(v))
    return(collect)

def qpcr(path, size : int =384, metadatalist: list = [] ):
    """
    Return three data frames: results, samples and melt curve.
    If melt curve is absent, return None.
    """
    results = pd.read_excel(path,
                            sheet_name="Results",
                            header=None)
    startrow = [i for i, v in enumerate(results[0].values) if v == "Well"][0]
    startcol = 0

    results = pd.DataFrame(results.values[startrow+1:startrow+ size+1,:],
                           columns=results.values[startrow,:])
    try:
        samples = pd.read_excel(path,
                                header=None,
                                sheet_name="Sample Setup"
                                )
        for i, v in  enumerate(samples[0].values):
            if type(v) is not str:
                break
        samples = pd.DataFrame(samples.values[i+2:,:],
                               columns = samples.values[i+1,:])
        samples["Row"] = [v[0] for v in samples["Well Position"]]
        samples["Column"] = [int(v[1:]) for v in samples["Well Position"]]
    except:
        samples = None
    amplification = pd.read_excel(path,
                                  header=None,
                                  sheet_name="Amplification Data")
    for i, v in  enumerate(amplification[0].values):
        if type(v) is not str:
            break
    amplification = pd.DataFrame(amplification.values[i+2:,:],
                           columns = amplification.values[i+1,:])
    if samples is not None:
        amplification = amplification.merge(samples[["Well","Well Position"]].drop_duplicates(),
                                            on="Well")
    amplification["Row"] = [v[0] for v in amplification["Well Position"]]
    amplification["Column"] = [int(v[1:]) for v in amplification["Well Position"]]
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
    if "CT" in results.columns:
        results["CT"] = fixup_ct(results.CT, results["Baseline End"].max())

    elif "Cq" in results.columns:
        results["CT"] = fixup_ct(results["Cq"], results["Baseline End"].max())
        results["Ct Threshold"] = results["Threshold"]
        amplification.rename({"dRn":"Delta Rn",
                              "Cycle Number":"Cycle"}, 
                             axis="columns", inplace=True)

    amplification = amplification.merge(amplification.groupby(["Well"]).apply(classify).reset_index(),
                                        on="Well")
    results = results.merge(amplification[["Well","prediction"]].drop_duplicates(),
                            on="Well")
    return(results, samples, meltcurve, amplification)

def process_metadata(meta, metaorder, keep_blanks=False,defaultdtype="int"):
    """
    Process a list of lists or numpy arrya that an be interpreted as a metadata table
    :params:
       - meta:  List of Lists
       - metaorder: string of column names separated by ':'
       - keep_blanks: Boolean, controls if blank entries are scrubbed. Default: False
       - defaultdtype: string, Sets the return type of every column uniformly. To supprese type conversion, set to None.
    """
    meta = np.array(meta)
    numcolumns = meta.shape[1]
    if ":" in metaorder:
        columns = metaorder.split(":")
    else:
        columns = [metaorder]
    mdf = pd.DataFrame(meta[0:,1:], 
                       index=pd.Index(meta[:,0]),
                       columns=list(range(1,numcolumns))).reset_index()\
                       .rename({"index":"Row"}, axis="columns")
    mdf = mdf.melt(id_vars="Row",value_vars=mdf.columns,
                   value_name=metaorder,
                   var_name="Column")
    if ":" in metaorder:
        expanded = mdf[metaorder].str.split(":",expand=True)
        for colid, col in enumerate(columns):
            mdf[col] = expanded[colid]
    if not keep_blanks:
        mdf = mdf[(mdf[metaorder] != '')]
    if defaultdtype is not None:
        for col in columns:
            mdf[col] = mdf[col].astype(defaultdtype)
    return(mdf)


def quadrantExplode(well96, preserve_source=False):

    """
    :params:  DataFrame 
    |Row (A-H) |Column (1-12)| Attributes |
    :returns: DataFrame 
    |Row (A-P) |Column (1-24)| Attributes |
    such that
    """
    collect = []
    for i, sourcerow in well96.iterrows():
        wellid = wellmapper96[(wellmapper96.Row == sourcerow.Row)\
                              & (wellmapper96.Column == sourcerow.Column)].well_number.values[0]
        fixedcoloffset = ((wellid -1)// 8)*32
        dest1, dest2, dest3, dest4 = \
            fixedcoloffset + (wellid  - (((wellid - 1)) // 8) * 8)*2 -1,\
            fixedcoloffset + (wellid  - (((wellid - 1)) // 8) * 8)*2 ,\
            fixedcoloffset +(wellid  - (((wellid - 1)) // 8) * 8)*2 + 15,\
            fixedcoloffset + (wellid  - (((wellid - 1)) // 8) * 8)*2 + 16
        attribute_columns = [c for c in well96.columns if c not in ["Row","Column"]]
        for rep, d in enumerate([dest1, dest2, dest3, dest4]):
            row = wellmapper384[wellmapper384.well_number  == d]
            entry = {"Row":row.Row.values[0],
                     "Column":row.Column.values[0], 
                     "well_number":d,
                     "replicate":rep+1,
                     "Row_Source":sourcerow.Row,
                     "Column_Source":sourcerow.Column}
            """
            copy over other attributes for each well
            """
            for col in attribute_columns:
                entry[col] = sourcerow[col]

            collect.append(entry)
    well384 = pd.DataFrame(collect)
    export_columns = well384.columns

    if not preserve_source:
        well384 = well384[[c for c in export_columns if "_Source" not in c]]

    return(well384)

def generateQSLayout(well384: pd.DataFrame, outpath : str, groups=None):
    columns = ["Well","Well Position","Sample Name","Sample Color",
               "Biogroup Name","Biogroup Color","Target Name",
               "Target Color","Task","Reporter","Quencher","Quantity","Comments"]
    collect = []
    for i, row in well384.iterrows():
        if groups is not None:
            if type(row[groups]) is not int:
                print("Groups must of type int!")
            else:
                c = colors[row[groups]]
                t = row[groups]
        else:
            c = """RGB(64,58,58)"""
            t=row.well_number
        entry = {"Well":row.well_number,
                 "Well Position": f"{row.Row}{row.Column}",
                 "Sample Name":f"Sample {row.well_number}",
                 "Sample Color":c,
                 "Biogroup Name":"",
                 "Biogroup Color":"",
                 "Target Name":f"Target {t}",
                 "Target Color":c,
                 "Task":"UNKNOWN",
                 "Reporter":"FAM",
                 "Quencher":"NFQ-MGB",
                 "Quantity":"",
                 "Comments":"",
                 }
        collect.append(entry)
    df = pd.DataFrame(collect)
    df.to_csv(outpath, index=False)
        

