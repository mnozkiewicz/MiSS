# How to run the simulation?
- We Have chosen to execute runepanet command not via epyt API, but rather using runepanet command and subprocesses. This approach is way more efficient and allows to use collected data from different runs.
# What are the parameters of simulations we run?
- The parameters of the simulation are being set via epyt API
- As simulation running is computationally costly, we decided to perform 24-hour simulations with 10 minute steps and reporting pressures every 6 hours.
- Those collected reports con be then converted to pandas dataframes and used for KNNs training.
- Leak in the network appears randomly through simulation. Its time can be used to get rid of data from timestamps where there is no leak. In consequence, every report contains from 1 to 4 datasets with leak.
- Base demands in for inp. file are taken from provided example data. They are then multiplied by random number from normal distribution with `μ = 1` and `σ = 0.1`
- for the node where leak appears, demand is multiplied by 3 instead.
# What do we collect from simulation?
- We collect report with obtained pressures values from every node. This can be further refined and used for KNN classificator.
### data refinement
- In order to convert EPANET report format to pandas we have to cut its header, separate it by timestamps, choose only those, that are after leak occurence and remove tails.
- We then replace series of whitespaces, except newline, in those mini-reports by `;` sign in order to read these data as `.csv` format into `pandas.Dataframe`

-example of report header:
```
Node Results at .*? hrs:
  ----------------------------------------------
                     Demand      Head  Pressure
  Node                  L/s         m         m
  ----------------------------------------------
  ```

  # KNN and Simulated Annealing

  So we've implemented the basic pipeline, which loads the data from the EPANET runs and a graph dscribing the network. The search for the optimal sensor placement is then conducted via Simulated Annealing algorithm. Each candidate solution in the Annealing algorithm is evaluated using KNN classifier. The whole pipeline is show in this [notebook](../notebooks/leak_prediction.ipynb).