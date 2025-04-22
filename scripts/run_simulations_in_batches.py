import os
import shutil
from epyt import epanet
from .prepare_files import prepare_files
from .run_simulations import run_simulations


def run_simulations_in_batches(
        file_path: str, 
        leaks_path: str, 
        reports_path: str,
        batch_size: int = 10,
        leaks_per_node: int = 10
    ) -> None:

    G = epanet(file_path)

    node_indexes = G.getNodeIndex()
    start, end = 0, batch_size

    while start < len(node_indexes):
        node_leak_list = list(node_indexes[start:end])
        # Generating new files
        prepare_files(
            file_path, 
            leaks_path, 
            leaks_per_node=leaks_per_node, 
            leak_node_ids=node_leak_list
        )

        # Generating reports from files currently in leaks folder
        run_simulations(leaks_path, reports_path)

        # Removing current leaks files
        shutil.rmtree(leaks_path)

        start, end = start + batch_size, end + batch_size


if __name__ == "__main__":
    input_file = "data/Hanoi.inp"
    leaks_path = "data/leaks"
    reports_path = "data/reports"
    run_simulations_in_batches(input_file, leaks_path, reports_path)
