#!/usr/bin/env python3
"""
Script to train and verify persistence in Python
"""

import os
import sys
import time
import subprocess


def run_command(command):
    """Run a shell command and print output"""
    print(f"\n=== Running: {command} ===")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0


def main():
    """Main function to train and verify persistence"""
    print("=== Training and Verifying Persistence ===")

    # Reset and train
    print("\n=== Resetting and Training ===")
    if not run_command("python app/reset_and_train.py"):
        print("Error resetting and training")
        return False

    # Check documents
    print("\n=== Checking Documents ===")
    if not run_command("python app/check_documents.py"):
        print("Error checking documents")
        return False

    # Restart the application (simulate container restart)
    print("\n=== Simulating Restart ===")
    print("Waiting 5 seconds...")
    time.sleep(5)

    # Check documents again after "restart"
    print("\n=== Checking Documents After Restart ===")
    if not run_command("python app/check_documents.py"):
        print("Error checking documents after restart")
        return False

    print("\n=== Training and Verification Complete ===")
    print(
        "If you see the same documents before and after restart, persistence is working correctly!"
    )
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
