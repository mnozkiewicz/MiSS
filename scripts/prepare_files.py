from epyt import epanet
from copy import deepcopy
from typing import Optional
import numpy as np
import os

TIME_STEP = 600  # 600 seconds - 10 mins
REPORTING_STEP = TIME_STEP * 36  # 6 hours
N_STEPS = 6 * 24  # 24 hours


def generate_leak_scale(low: float, high: float, size: int) -> np.ndarray:
    return np.random.uniform(low, high, size)


def prepare_single_file(G: epanet, leaks_path: str, leak_node_id: int, leak_scale: float = 3.0) -> None:
    node_name = G.getNodeNameID(leak_node_id)
    leak_start = np.random.randint(
        low=1, high=N_STEPS
    )  # We assume leaks starts randomly through the simulation

    first_relevant_timestamp = int(leak_start / N_STEPS * 4) + 1
    # raise Exception
    # leak_node_id = '10'  # Node ids not always have to be numeric and its something different that nodes index
    # leak_node_index = G.getNodeIndex(leak_node_id)

    leak_pattern = np.random.normal(1, 0.1, size=(TIME_STEP * N_STEPS + 1,))
    leak_pattern[leak_start:] = leak_scale  # Multiply by leak_scale

    pattern_index = G.addPattern("leak", leak_pattern)  # Add demand pattern
    G.setNodeDemandPatternIndex(leak_node_id, pattern_index)
    G.setDemandModel("PDA", pmin=0, preq=0.1, pexp=0.5)
    # G.setNodeBaseDemands(leak_node_id, 50)
    G.saveInputFile(
        os.path.join(leaks_path, f"{node_name}_{first_relevant_timestamp}_{leak_scale:.2f}".replace('.', ',') + ".inp")
    )
    G.deletePattern("leak")


def prepare_files(
        file_path: str, 
        leaks_path: str, 
        leaks_per_node: int = 1,
        leak_node_ids: Optional[list[int]] = None,
        generate_baseline: bool = True
    ):

    G = epanet(file_path)
    G.setTimeReportingStep(REPORTING_STEP)
    G.setTimeSimulationDuration(TIME_STEP * N_STEPS)  # 24 hours
    G.setTimePatternStep(TIME_STEP)  # Same as reporting step

    if not os.path.exists(leaks_path):
        os.makedirs(leaks_path)
    
    G.setDemandModel("PDA", pmin=0, preq=0.1, pexp=0.5)

    # Generate input with no leaks in order to know the baseline measures for the network
    # It is important for the machine learning algorithm later
    if generate_baseline:
        G.saveInputFile(
            os.path.join(leaks_path, f"baseline_1.inp")
        )

    if leak_node_ids is None:
        leak_node_ids = sorted(G.getNodeIndex())

    print(f"generating {len(leak_node_ids) * leaks_per_node} input files...")
    
    for leak_node_id in leak_node_ids:
        leak_scale_list = generate_leak_scale(2.0, 20.0, leaks_per_node)
        for leak_scale in leak_scale_list:
            prepare_single_file(G, leaks_path, leak_node_id, leak_scale)


if __name__ == "__main__":
    input_file = "data/Hanoi.inp"
    leaks_path = "data/leaks"
    prepare_files(input_file, leaks_path, leaks_per_node=20)
