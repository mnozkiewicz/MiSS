from scripts.prepare_files import prepare_files
from scripts.run_simulations import run_simulations

if __name__ == "__main__":
    leaks_path = "/home/wladek/MiSS_DATA/leaks"
    reports_path = "/home/wladek/MiSS_DATA/reports"
    prepare_files("../example1.inp", leaks_path)
    run_simulations(leaks_path, reports_path)
