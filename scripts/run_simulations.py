import os

os.environ["EPANET_HOME"] = "EPANET/build/bin/runepanet"  # NALEŻY DOSTOSOWAĆ

def run_simulations(leaks_path: str, reports_path: str) -> None:
    if "EPANET_HOME" not in os.environ:
        raise AttributeError(
            "You need to set 'EPANET_HOME environmental variable" \
            "It should point to EPANET executable"
        )

    epanet_executable_path = os.environ["EPANET_HOME"]

    inp_files = os.listdir(leaks_path)
    if not os.path.exists(reports_path):
        os.mkdir(reports_path)
        
    for file in inp_files:
        name = file.split(".")[0]
        in_path = os.path.join(leaks_path, file)
        out_path = os.path.join(reports_path, f"{name}.rpt")

        command = f"{epanet_executable_path} {in_path} {out_path}"

        if (p := os.system(command)) > 0:
            print(f"ERROR {p}")


if __name__ == "__main__":
    leaks_path = "data/leaks"
    reports_path = "data/reports"
    run_simulations(leaks_path, reports_path)
