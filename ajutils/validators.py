import pandas as pd
from pandera import DataFrameSchema, Column, Check
import pandera as pa

def validateProbeWorklist_96(df : pd.DataFrame,
                             row_name: str ="Row",
                             col_name: str="Column",
                             probe_id : int="probe_id",
                             ,
                             )\
                                -> None:
    """Validate a 96‑well probe worklist DataFrame.
    
     Parameters
     ----------
     df : pandas.DataFrame, required
         The DataFrame to validate. Pass the DataFrame you want
         validated.
     row_name : str, optional
         Name of the column containing row identifiers (default "Row"). Each value must be a
         single uppercase letter A–H.
     col_name : str, optional
         Name of the column containing column identifiers (default "Column"). Each value must be
         an integer in the range 1–12.
     probe_id : str, optional
         Name of the column containing the probe identifier (default "probe_id"). Expected to be
         a string (for example matching r'^[A-Z]*[0-9]*$' if you require that format).
     Returns
     -------
     None
         The function is intended to validate the DataFrame in-place (or raise on failure) and
         does not return a DataFrame.
    
     Raises
     ------
     ValueError
         If required columns are missing or arguments are of the wrong type.
     pandera.errors.SchemaError
         If schema validation fails (if using pandera to perform the checks).
    
     Notes
     -----
     - The docstring assumes the function checks that row/column values fall within the 96‑well
       plate limits (rows A–H, columns 1–12) and that probe_id is present and correctly typed.
     - If the implementation uses pandera with coerce=True, input columns may be coerced to the
       expected dtypes before checks are applied.
     - Do not rely on a mutable default DataFrame in production; pass an explicit DataFrame object.
    
     Examples
     --------
     validateProbeWorklist_96(df=my_df)
     validateProbeWorklist_96(row_name='R', col_name='C', probe_id='ProbeID', df=my_df)
    """
    schema = pa.DataFrameSchema(
        {
            row_name: Column(pa.String, checks=Check.str_matches(r"^[A-H]$"), nullable=False),
            col_name: Column(pa.Int, checks=Check.in_range(1, 12), nullable=False),
            probe_name: Column(pa.String, checks=Check.str_matches(r"^[A-Z]*[0-9]*$"), nullable=False),
            org_name: Column(pa.String, nullable=False),
        },
        coerce=True)
    schema.validate(df)


def validateSampleTransfer_384(row_name: str ="Row",
                                col_name: str="Column",
                                probe_name :str="Probe_ID",
                                org_name : str="Organism")\
                                -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        {
            row_name: Column(pa.String, checks=Check.str_matches(r"^[A-H]$"), nullable=False),
            col_name: Column(pa.Int, checks=Check.in_range(1, 12), nullable=False),
            probe_name: Column(pa.String, checks=Check.str_matches(r"^[A-Z]*[0-9]*$"), nullable=False),
            org_name: Column(pa.String, nullable=False),
        },
        coerce=True)




# schema = DataFrameSchema(
#     {
#         ROW: Column(
#             pa.String,
#             checks=Check.str_matches(r"^[A-H]$"),
#             nullable=False,
#         ),
#         COL: Column(
#             pa.Int,
#             checks=Check.in_range(1, 12),
#             nullable=False,
#         ),
#         PROBE: Column(
#             pa.String,
#             checks=Check.str_matches(r"^[A-Z]*[0-9]*$"),
#             nullable=False,
#         ),
#         ORG: Column(pa.String, nullable=False),
#     },
#     coerce=True,
# )

