import pandas as pd
import dataframe_image as dfi
from .colors import colorsrgb
from itertools import product

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

def makePlate(df: pd.DataFrame, annotatecol : str,
              outfilename : str = "temp.png",
              rowCol :str="Row", colCol : str = "Column") -> None:
    import seaborn as sns
    import matplotlib.pyplot as plt

    plate = pd.pivot(df, index=rowCol,
                     columns=colCol,
                     values=annotatecol)
    colorwells = {row[annotatecol]:colorsrgb[i] for i, row in\
                  df[[annotatecol]].drop_duplicates().reset_index(drop=True).iterrows()}

    def applycolor(val):
        r, g, b = colorwells[val]
        hexs = f"#{r:02x}{g:02x}{b:02x}"
        return(f'color : {hexs}')

    dfi.export(plate.style.map(applycolor), 
               outfilename,
               table_conversion="matplotlib")


def fixup_96(df):
    for i,row in wellmapper96.iterrows():
        if df[(df.Row == row.Row) & (df.Column == row.Column)].shape[0] == 0:
            df = pd.concat([df, pd.DataFrame({"Row":[row.Row],
                                              "Column":[row.Column]})],
                           ignore_index=True).reset_index(drop=True)
    return(df)
