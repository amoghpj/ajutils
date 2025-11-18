import pandas as pd

def indexColumn(df: pd.DataFrame, 
                column: str,
                indexname : str = "idx") -> pd.DataFrame:
    """
    Generate a dataframe that pulls out `column`, and reindexes it.
    """
    if column not in df.columns:
        raise KeyError(f"{column} not found in dataframe")
    else:
        idxdf = df[[column]].drop_duplicates()\
            .reset_index(drop=True)\
            .reset_index()\
            .rename({"index":indexname}, axis=1)
        return idxdf
