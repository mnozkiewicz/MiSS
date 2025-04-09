from scripts.prepare_files import prepare_files
from scripts.run_simulations import run_simulations

if __name__ == "__main__":
    leaks_path = "data/leaks"
    reports_path = "data/reports"
    network_path = "data/Hanoi.inp" # Hanoi network rather small

    prepare_files(network_path, leaks_path)
    run_simulations(leaks_path, reports_path)
