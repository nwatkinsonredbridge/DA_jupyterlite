import pandas as pd
from glob import glob
import json
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import os

###########################################
current_directory = os.path.dirname(os.path.abspath(__file__))
with open(f"{current_directory}/EXPORT_2023/D_companies_new.json", 'r') as f:
    D_companies = json.load(f)

D_companies_rev = {}
D_companies_copy = {}
for d in list(D_companies.keys()):
    zipname = D_companies[d]["zipfile"].split("/")[-1].replace(".zip","")
    D_companies_copy[d] = zipname
    D_companies_rev[zipname] = d
    D_companies_copy[d] = "EXPORT_2023/RAW_CLEANUP/"


def read_excel_file(d):
    """Reads an Excel file and returns a tuple (company_name, dataframe)."""
    zipname = d.split("/")[-1].replace("_output.xlsx", "")
    company_name = D_companies_rev[zipname]
    df = pd.read_excel(d)
    return company_name, df

def load_environment():
    d_files = "EXPORT_2023/EXTRACTED/*.xlsx"
    dfiles = glob(d_files)

    # Initialize the dictionary to store data
    D_data = {}

    # Use ThreadPoolExecutor for parallel reading
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(read_excel_file, dfiles), total=len(dfiles), desc="Reading files"))

    # Store the results in the dictionary
    for company_name, dataframe in results:
        D_data[company_name] = dataframe
    return D_data