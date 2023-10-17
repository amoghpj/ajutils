from io import StringIO
from Bio import SeqIO, Seq
import pandas as pd

def read_gff(p):
    """
    :returns: pandas DataFrame
    """
    df = pd.read_csv(p, sep="\t",
                     names=["seqname","source","feature","start","end", "score","strand","frame","attribute"],
                     comment="#",
                     skiprows=[0])
    print(df.head(3))
    return(df)

def read_gb(path):
    with open(p, "r") as infile:
        contigs = "".join(list(infile.readlines())).split("\n//\n")
        for contig in [c for c in dat if len(c)> 0]:
            rec = list(SeqIO.parse(StringIO(contig),"genbank"))[0]
            if len(rec) > 1e5:
                loci[rec.id] = rec    
    gb = SeqIO.read(path, "genbank")
    return(gb)
