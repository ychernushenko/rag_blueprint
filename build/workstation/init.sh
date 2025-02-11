#!/bin/bash

# Read environment name from command line arguments
if [ "$1" = "--env" ] && [ -n "$2" ]; then
    env="$2"
    echo "Environment: $env"
else
    echo "Please provide the environment name as an argument. E.g. './init.sh --env dev'"
    exit 1
fi

# Setup initialization variables
current_epoch=$(date +%s)
build_name="build-${current_epoch}"

log_dir="build/workstation/logs"
log_file="${log_dir}/${build_name}.log"
mkdir -p $log_dir

# Check virtual environment, python and pip are setup
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate the virtual environment before running the initialization script."
    exit 2
fi

if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Please install uv and try again."
    exit 3
fi

# Install required packages
echo "Installing required packages"

uv sync --all-extras

# Run initialization
echo "Running initialization script in the background. You can find live logs at ${log_file}"

nohup python build/workstation/runner.py \
    --build-name $build_name \
    --log-file $log_file  \
    --env $env \
    --init \
    > $log_file &

# nohup_pid=$!
# echo "Process ID: $nohup_pid"
