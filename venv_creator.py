#!/usr/bin/env python3
"""
Python Virtual Environment Creator

This script creates and configures Python virtual environments with specified packages.
It deliberately avoids using Anaconda/conda even if installed on the system.

Usage:
    python venv_creator.py --name myenv --packages "numpy pandas scikit-learn"
    python venv_creator.py --name myenv --packages "numpy pandas" --requirements requirements.txt
    python venv_creator.py --name project_env --python python3.9
"""

import argparse
import os
import subprocess
import sys
import platform
from pathlib import Path

def run_command(command, shell=False):
    """Run a shell command and print output."""
    print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, text=True)
        else:
            result = subprocess.run(command, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False

def check_venv_module():
    """Check if the venv module is available."""
    try:
        import venv
        return True
    except ImportError:
        return False

def check_virtualenv_installed():
    """Check if virtualenv is installed."""
    try:
        subprocess.run(["virtualenv", "--version"], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_venv(env_name, python_path=None):
    """Create a virtual environment using venv or virtualenv."""
    env_path = Path(env_name)
    
    if env_path.exists():
        response = input(f"Environment '{env_name}' already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Operation cancelled.")
            return False
        
        # Remove existing environment
        if platform.system() == "Windows":
            run_command(f"rmdir /s /q {env_name}", shell=True)
        else:
            run_command(["rm", "-rf", env_name])
    
    has_venv = check_venv_module()
    has_virtualenv = check_virtualenv_installed()
    
    if python_path:
        # Use specified Python interpreter
        if has_virtualenv:
            return run_command(["virtualenv", "-p", python_path, env_name])
        elif has_venv:
            return run_command([python_path, "-m", "venv", env_name])
        else:
            print("Error: Cannot use specified Python interpreter without venv or virtualenv")
            return False
    else:
        # Use default Python interpreter
        if has_venv:
            return run_command([sys.executable, "-m", "venv", env_name])
        elif has_virtualenv:
            return run_command(["virtualenv", env_name])
        else:
            print("Error: Neither 'venv' module nor 'virtualenv' package is available.")
            print("Please install virtualenv: pip install virtualenv")
            return False

def install_packages(env_name, packages=None, requirements_file=None):
    """Install packages into the virtual environment."""
    if not packages and not requirements_file:
        return True
    
    # Determine the pip path based on the platform
    if platform.system() == "Windows":
        pip_path = os.path.join(env_name, "Scripts", "pip")
    else:
        pip_path = os.path.join(env_name, "bin", "pip")
    
    # Upgrade pip first
    run_command([pip_path, "install", "--upgrade", "pip"])
    
    if packages:
        package_list = packages.split()
        return run_command([pip_path, "install"] + package_list)
    
    if requirements_file:
        requirements_path = Path(requirements_file)
        if not requirements_path.exists():
            print(f"Error: Requirements file '{requirements_file}' not found.")
            return False
        return run_command([pip_path, "install", "-r", requirements_file])

def print_activation_instructions(env_name):
    """Print instructions for activating the virtual environment."""
    env_path = os.path.abspath(env_name)
    
    print("\n" + "="*50)
    print(f"Virtual environment '{env_name}' created successfully!")
    print("="*50)
    print("\nTo activate the environment:")
    
    if platform.system() == "Windows":
        print(f"    source {env_name}/Scripts/activate")
    else:
        print(f"    source {env_name}/bin/activate")
    
    print("\nTo deactivate the environment:")
    print("    deactivate")
    print("\nTo delete this environment, simply remove the directory:")
    if platform.system() == "Windows":
        print(f"    rmdir /s /q {env_name}")
    else:
        print(f"    rm -rf {env_name}")
    print("="*50)

def main():
    """Main function to parse arguments and create virtual environment."""
    parser = argparse.ArgumentParser(description="Create a Python virtual environment")
    parser.add_argument("--name", required=True, help="Name of the virtual environment")
    parser.add_argument("--packages", help="Space-separated list of packages to install")
    parser.add_argument("--requirements", help="Path to requirements.txt file")
    parser.add_argument("--python", help="Python interpreter to use (e.g., python3.9)")
    
    args = parser.parse_args()
    
    if create_venv(args.name, args.python):
        packages_installed = install_packages(args.name, args.packages, args.requirements)
        if packages_installed:
            print_activation_instructions(args.name)
            return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())