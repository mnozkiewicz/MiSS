import pandas as pd
import numpy as np
import scripts
import os


def extract_node_id(path: str) -> int:
    normpath = os.path.normpath(path)
    filename = normpath.split("/")[-1]
    return int(filename.split("_")[0])


def report_to_pandas(report: list[pd.DataFrame], leakage_node: int) -> pd.DataFrame:

    training_example = []
    for i, pressure_measure in enumerate(report):
        pressure_measure = pressure_measure.T.reset_index(drop=True)
        pressure_measure.columns.name = None

        pressure_measure["ts"] = i
        pressure_measure["leakage_node"] = leakage_node

        training_example.append(pressure_measure)

    row_df = pd.concat(training_example)
    return row_df

def transform_whole_dataset(reports: list[tuple[list[pd.DataFrame], int]]) -> pd.DataFrame:
    report_dataframes = []

    for report in reports:
        report_dataframes.append(report_to_pandas(*report))

    df = pd.concat(report_dataframes).reset_index(drop=True)
    return df


def read_pressures(report_dir_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    filenames = os.listdir(report_dir_path)

    report_paths = [os.path.join(report_dir_path, filename) for filename in filenames if not filename.startswith("baseline")]
    reports = [(scripts.read_report(path), extract_node_id(path)) for path in report_paths]
    baseline_report = scripts.read_report(os.path.join(report_dir_path, "baseline_1.rpt"))

    df = transform_whole_dataset(reports)
    baseline_pressures = report_to_pandas(baseline_report, -1)
    baseline_pressures = baseline_pressures.iloc[[0]].drop(columns=["ts", "leakage_node"]).to_numpy()
    ts, leakage_node = df["ts"], df["leakage_node"]
    pressures = df.drop(columns=["ts", "leakage_node"]).to_numpy()

    pressures = pressures - baseline_pressures

    return pressures, leakage_node.to_numpy(), ts.to_numpy()
