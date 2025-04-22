import io
import os.path
import re
import pandas as pd

header = """Node Results at .*? hrs:
  ----------------------------------------------
                     Demand      Head  Pressure
  Node                  L/s         m         m
  ----------------------------------------------"""
tail = "  Reservoir"
sep = "[ |\t]+"


def read_report(report_path: str):
    with open(report_path) as raport:
        data = raport.read()
    data_hours = re.findall(
        "Node Results at .*? hrs:.*?Reservoir", data, flags=re.DOTALL
    )
    data_hours = [
        re.sub(sep, ";", re.sub(header, "", re.sub(tail, "", i))) for i in data_hours
    ]
    first_relevant_timestamp = int(
        os.path.basename(report_path).split(".")[0].split("_")[1]
    )
    hourly_datasets = []
    for data_string in data_hours[first_relevant_timestamp:]:
        df = pd.read_csv(io.StringIO(data_string), sep=";", header=None, usecols=[1, 4])
        df = df.rename(columns={1: "node", 4: "pressure"})
        df = df.set_index("node")
        hourly_datasets.append(df)
    return hourly_datasets


if __name__ == "__main__":
    file_path = "../J49373_4.rpt"
    hourly_datasets = read_report(file_path)
    print(len(hourly_datasets))
    for df in hourly_datasets:
        print(df)
