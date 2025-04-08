import os

EPANET_HOME = "/home/wladek/EPANET/build/bin/runepanet"  # NALEŻY DOSTOSOWAĆ


def run_simulations(leaks_path, reports_path):
    inp_files = os.listdir(leaks_path)
    if not os.path.exists(reports_path):
        os.mkdir(reports_path)
    for file in inp_files:
        name = file.split(".")[0]
        in_path = os.path.join(leaks_path, file)
        out_path = os.path.join(reports_path, f"{name}.rpt")

        command = f"{EPANET_HOME} {in_path} {out_path}"

        if (p := os.system(command)) > 0:
            print(f"ERROR {p}")


if __name__ == "__main__":
    leaks_path = "/home/wladek/MiSS_DATA/leaks"
    reports_path = "/home/wladek/MiSS_DATA/reports"
    run_simulations(leaks_path, reports_path)
