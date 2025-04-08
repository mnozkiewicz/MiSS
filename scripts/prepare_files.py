from epyt import epanet
import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np
import os

TIME_STEP = 600  # 600 seconds - 10 mins
REPORTING_STEP = TIME_STEP * 36  # 6 hours
N_STEPS = 6 * 24  # 24 hours


def prepare_files(file_path, leaks_path):
    G = epanet(file_path)

    G.setTimeReportingStep(REPORTING_STEP)
    G.setTimeSimulationDuration(TIME_STEP * N_STEPS)  # 24 hours
    G.setTimePatternStep(TIME_STEP)  # Same as reporting step
    if not os.path.exists(leaks_path):
        os.mkdir(leaks_path)
    print(f"generating {len(G.getNodeIndex())} input files...")
    for leak_node_id in G.getNodeIndex():
        node_name = G.getNodeNameID(leak_node_id)
        leak_start = np.random.randint(
            low=1, high=N_STEPS
        )  # We assume leaks starts randomly through the simulation
        first_relevant_timestamp = int(leak_start / N_STEPS * 4) + 1
        # raise Exception
        # leak_node_id = '10'  # Node ids not always have to be numeric and its something different that nodes index
        # leak_node_index = G.getNodeIndex(leak_node_id)

        leak_pattern = np.random.normal(1, 0.1, size=(TIME_STEP * N_STEPS + 1,))
        leak_pattern[leak_start:] = 3  # Multiply by 3

        pattern_index = G.addPattern("leak", leak_pattern)  # Add demand pattern
        G.setNodeDemandPatternIndex(leak_node_id, pattern_index)
        G.setDemandModel("PDA", pmin=0, preq=0.1, pexp=0.5)
        # G.setNodeBaseDemands(leak_node_id, 50)
        G.saveInputFile(
            os.path.join(leaks_path, f"{node_name}_{first_relevant_timestamp}.inp")
        )
        G.deletePattern("leak")


if __name__ == "__main__":
    input_file = "example1.inp"
    leaks_path = "/home/wladek/MiSS_DATA/leaks"
    prepare_files(input_file, leaks_path)
