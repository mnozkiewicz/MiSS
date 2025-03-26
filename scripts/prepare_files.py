from epyt import epanet
import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np
import os
TIME_STEP = 600 # 600 seconds - 10 mins
N_STEPS = 6 * 48

if __name__ == "__main__":
    print(os.getcwd())
    input_file = "example1.inp"
    G = epanet(input_file)

    G.setTimeReportingStep(TIME_STEP)
    G.setTimeSimulationDuration(TIME_STEP * N_STEPS)  # 48 hours
    G.setTimePatternStep(TIME_STEP)  # Same as reporting step
    if not os.path.exists('leaks'):
        os.mkdir('leaks')
    print(len(G.getNodeIndex()))
    for leak_node_id in G.getNodeIndex():
        leak_start = np.random.randint(low=1, high=6 * 48)  # We assume leaks starts randomly through the simulation
        # raise Exception
        # leak_node_id = '10'  # Node ids not always have to be numeric and its something different that nodes index
        # leak_node_index = G.getNodeIndex(leak_node_id)

        leak_pattern = np.ones(TIME_STEP * N_STEPS + 1)
        leak_pattern[leak_start:] = 3  # Multiply by 3

        pattern_index = G.addPattern('leak', leak_pattern)  # Add demand pattern
        G.setNodeDemandPatternIndex(leak_node_id, pattern_index)
        # G.setNodeBaseDemands(leak_node_id, 50)
        G.saveInputFile(f"leaks/example1_{leak_node_id}.inp")
        G.deletePattern('leak')
