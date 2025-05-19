#!/bin/bash
#SBATCH --job-name=epanet_array
#SBATCH --output=logs/epanet_%A_%a.out
#SBATCH --error=logs/epanet_%A_%a.err
#SBATCH --array=0-99
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:03:00
#SBATCH --partition=plgrid

# CONFIGURATION
# Total number of jobs
TOTAL_JOBS=2237
# Number of Slurm array tasks
ARRAY_TASKS=100
LEAKS_PATH="$SCRATCH/MISS_INPUT"
REPORTS_PATH="$SCRATCH/MISS_OUTPUT"
EPANET_EXECUTABLE="runepanet"

# Ensure reports directory exists
mkdir -p "$REPORTS_PATH"

# Number of jobs per array task (ceil division)
JOBS_PER_TASK=$(( (TOTAL_JOBS + ARRAY_TASKS - 1) / ARRAY_TASKS ))

# Calculate the range of jobs for this array task
START_INDEX=$(( SLURM_ARRAY_TASK_ID * JOBS_PER_TASK ))
END_INDEX=$(( START_INDEX + JOBS_PER_TASK - 1))

# Clamp to total number of jobs
if [ $END_INDEX -ge $TOTAL_JOBS ]; then
    END_INDEX=$(( TOTAL_JOBS - 1 ))
fi

# Get list of .inp files
mapfile -t INP_FILES < <(find "$LEAKS_PATH" -maxdepth 1 -name "*.inp" | sort)

echo "Processing indices from $START_INDEX to $END_INDEX"

for i in $(seq $START_INDEX $END_INDEX); do
    echo "Processing input file $i"
    # Get the file for this array task
    INP_FILE="${INP_FILES[$i]}"

    # If file doesn't exist (in case array range > number of files), exit safely
    if [ -z "$INP_FILE" ]; then
      echo "No .inp file found for ID=$i"
      exit 0
    fi
    # Extract filename without extension
    BASENAME=$(basename "$INP_FILE" .inp)
    OUT_FILE="$REPORTS_PATH/$BASENAME.rpt"

    # Run EPANET
    echo "Running EPANET on $INP_FILE"
    "$EPANET_EXECUTABLE" "$INP_FILE" "$OUT_FILE"

done

# Optional: check status
if [ $? -ne 0 ]; then
    echo "EPANET run failed for $INP_FILE"
else
    echo "EPANET run completed: $OUT_FILE"
fi




