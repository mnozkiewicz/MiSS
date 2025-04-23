#!/bin/bash
#SBATCH --job-name=epanet_array
#SBATCH --output=logs/epanet_%A_%a.out
#SBATCH --error=logs/epanet_%A_%a.err
#SBATCH --array=0-99
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:30:00
#SBATCH --partition=plgrid

# CONFIGURATION
LEAKS_PATH="./MISS_DATA"
REPORTS_PATH="./MISS_OUTPUT"
EPANET_EXECUTABLE="runepanet"

# Ensure reports directory exists
mkdir -p "$REPORTS_PATH"

# Get list of .inp files
mapfile -t INP_FILES < <(find "$LEAKS_PATH" -maxdepth 1 -name "*.inp" | sort)

# Get the file for this array task
INP_FILE="${INP_FILES[$SLURM_ARRAY_TASK_ID]}"

# If file doesn't exist (in case array range > number of files), exit safely
if [ -z "$INP_FILE" ]; then
    echo "No .inp file found for SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID"
    exit 0
fi

# Extract filename without extension
BASENAME=$(basename "$INP_FILE" .inp)
OUT_FILE="$REPORTS_PATH/$BASENAME.rpt"

# Run EPANET
echo "Running EPANET on $INP_FILE"
"$EPANET_EXECUTABLE" "$INP_FILE" "$OUT_FILE"

rm "$INP_FILE"

# Optional: check status
if [ $? -ne 0 ]; then
    echo "EPANET run failed for $INP_FILE"
else
    echo "EPANET run completed: $OUT_FILE"
fi

