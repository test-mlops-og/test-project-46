#!/usr/bin/env python3

import sys
import os
import subprocess

# Function to install dependencies
def install(package):
    print(f"Installing {package}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        check=False,  # Don't raise an exception immediately
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Failed to install {package}. Error:\n{result.stderr}")
        sys.exit(1)

# Ensure required packages are installed
try:
    import yaml
    import sagemaker
except ImportError:
    install("pyyaml")
    install("sagemaker")
    import yaml
    import sagemaker

# Import the get_pipeline function from the appropriate module.
from pipelines.abalone.pipeline import get_pipeline

def main():
    config_file = os.getenv("CONFIG_PATH", "config.yaml")

    # Load configuration from YAML file.
    try:
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    # Define required keys that must be present in the config.
    required_keys = ["region", "role", "tracking_server_arn"]
    pipeline_kwargs = {}

    for key in required_keys:
        if key not in config:
            print(f"Error: Required key '{key}' not found in {config_file}.")
            sys.exit(1)
        pipeline_kwargs[key] = config[key]

    # Define optional keys which may or may not be present.
    optional_keys = [
        "sagemaker_project_name", "default_bucket", "model_package_group_name",
        "pipeline_name", "base_job_prefix", "processing_instance_type", "training_instance_type",
        "experiment_name", "max_jobs", "max_parallel_jobs", "strategy", "hyperparameters", "use_sg_model_registry"
    ]

    # Add any optional keys present in the config.
    for key in optional_keys:
        if key in config:
            pipeline_kwargs[key] = config[key]
    print(pipeline_kwargs)
    try:
        # Create and deploy the pipeline.
        pipeline = get_pipeline(**pipeline_kwargs)
        pipeline.upsert(role_arn=pipeline_kwargs['role'])
        pipeline.start()
        print("Pipeline created and started successfully.")
    except Exception as e:
        print(f"Error creating or starting pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
