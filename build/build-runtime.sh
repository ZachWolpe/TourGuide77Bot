#!/bin/bash

# Environment name
ENV_NAME="telegram-bot"

# Path to the YAML file
YAML_FILE="python-runtime.yml"

# Check if conda is available, otherwise use mamba
if command -v conda >/dev/null 2>&1; then
    CONDA_CMD="conda"
elif command -v mamba >/dev/null 2>&1; then
    CONDA_CMD="mamba"
else
    echo "Neither conda nor mamba found. Please install one of them."
    exit 1
fi

# Remove existing environment if it exists
echo "Removing existing environment if it exists..."
$CONDA_CMD env remove -n $ENV_NAME -y

# Create new environment
echo "Creating new environment..."
$CONDA_CMD env create -f $YAML_FILE

# Activate the new environment
echo "Activating new environment..."
source $($CONDA_CMD info --base)/etc/profile.d/conda.sh
$CONDA_CMD activate $ENV_NAME

echo "Environment $ENV_NAME is now active and ready to use."