#!/bin/bash
#SBATCH --job-name=epanet_array
#SBATCH --output=logs/output_%A_%a.out
#SBATCH --error=logs/error_%A_%a.err
#SBATCH --array=0-100
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00

# Define total jobs and how many array tasks we are running
TOTAL_JOBS=2237
ARRAY_TASKS=101
JOBS_PER_TASK=$(( (TOTAL_JOBS + ARRAY_TASKS - 1) / ARRAY_TASKS ))

START_INDEX=$(( SLURM_ARRAY_TASK_ID * JOBS_PER_TASK ))
END_INDEX=$(( START_INDEX + JOBS_PER_TASK - 1 ))

# Clamp end index to total jobs
if [ "$END_INDEX" -ge "$TOTAL_JOBS" ]; then
  END_INDEX=$(( TOTAL_JOBS - 1 ))
fi

echo "SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID: Processing files $START_INDEX to $END_INDEX"

for i in $(seq $START_INDEX $END_INDEX); do
    input_file="input_files/input_${i}.inp"
    output_file="output_files/output_${i}.out"

    echo "Processing $input_file..."

    # Replace with your actual command, e.g.:
    # ./run_epanet $input_file > $output_file
done