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
    """
    Utility wrapper around SeqIO.read(fname, "genbank").
    That function fails when there are multiple loci in a single
    genbank file. This function returns a list of Seq records
    :returns: list of Seq Records
    """
    with open(path, "r") as infile:
        contigs = "".join(list(infile.readlines())).split("\n//\n")
        loci = {}
        for contig in [c for c in contigs if len(c)> 0]:
            rec = list(SeqIO.parse(StringIO(contig),"genbank"))[0]
            loci[rec.id] = rec    
    return(loci)
