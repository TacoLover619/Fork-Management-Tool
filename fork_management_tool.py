# GitHub Fork Management Tool
# Author: Alan Hare (GitHub: [TacoLover619](https://github.com/TacoLover619))
# Language: Python
# License: MIT License
# Version: 1.0.0
# Date Created: 2025-01-10
# Last Updated: 2025-01-10
# Dependencies: requests, logging, sys, os
# Project URL: [Fork-Management-Tool](https://github.com/TacoLover619/Fork-Management-Tool)
#
# Description:
# A script to manage GitHub forks by listing forks, syncing branches, and automating pull requests.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided 
# that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions, and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions, and the following disclaimer 
#    in the documentation and/or other materials provided with the distribution.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS 
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF 
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import logging
import sys
import os

# Configure logging
logging.basicConfig(filename="error.log", level=logging.ERROR, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Environment variables
USERNAME = os.getenv("GITHUB_USERNAME")
TOKEN = os.getenv("GITHUB_TOKEN")
if not USERNAME or not TOKEN:
    user_profile = os.getenv("USERPROFILE")
    ps_profile_path = os.path.join(user_profile, "Documents", "PowerShell", "Microsoft.PowerShell_profile.ps1")
    print(f"Error: Set GITHUB_USERNAME and GITHUB_TOKEN in your PowerShell profile at {ps_profile_path}.")
    sys.exit(1)

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Utility functions
def log_error(e): logging.error(e)

def write_output(message, level="info"):
    levels = {"info": "[INFO]", "success": "[SUCCESS]", "error": "[ERROR]", "warning": "[WARNING]"}
    print(f"{levels.get(level, '[INFO]')} {message}")

def api_request(url, method="GET", data=None):
    try:
        headers = {"Authorization": f"token {TOKEN}"}
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"API request error: {e}")
        return None

# Core functionalities
def get_forks():
    return api_request(f"{GITHUB_API_URL}/user/repos?type=fork") or []

def get_branches(repo_name):
    return api_request(f"{GITHUB_API_URL}/repos/{repo_name}/branches") or []

def sync_branches(fork, original):
    original_branches = get_branches(original)
    if not original_branches:
        write_output(f"No branches found in original repo: {original}", "warning")
        return

    for branch in original_branches:
        branch_name = branch["name"]
        pr_data = {
            "head": f"{original}:{branch_name}",
            "base": branch_name,
            "title": f"Sync branch {branch_name}",
            "body": f"Syncing branch {branch_name} from {original}."
        }
        pr_url = f"{GITHUB_API_URL}/repos/{fork['full_name']}/pulls"
        response = api_request(pr_url, method="POST", data=pr_data)
        if response:
            write_output(f"Created PR for branch {branch_name} in {fork['full_name']}", "success")
        else:
            write_output(f"Failed to create PR for branch {branch_name}", "error")

def sync_all_forks():
    for fork in get_forks():
        original = fork.get("parent", {}).get("full_name")
        if original:
            write_output(f"Syncing branches from {original} to {fork['full_name']}...", "info")
            sync_branches(fork, original)
        else:
            write_output(f"Original repository not found for {fork['full_name']}", "warning")

# Menu and user interaction
def display_menu():
    print("\nGitHub Fork Management Menu")
    print("1. List all forks")
    print("2. List branches in a fork")
    print("3. Sync branches for a specific fork")
    print("4. Sync branches for all forks")
    print("5. Exit")

def handle_choice(choice):
    if choice == "1":
        forks = get_forks()
        if forks:
            for i, fork in enumerate(forks, 1):
                write_output(f"{i}. {fork['full_name']}", "success")
        else:
            write_output("No forks found.", "error")

    elif choice == "2":
        fork_name = input("Enter the full name of the fork (e.g., user/repo): ")
        branches = get_branches(fork_name)
        if branches:
            for branch in branches:
                write_output(f"- {branch['name']}", "success")
        else:
            write_output("No branches found.", "error")

    elif choice == "3":
        forks = get_forks()
        if not forks:
            write_output("No forks found.", "error")
            return

        for i, fork in enumerate(forks, 1):
            write_output(f"{i}. {fork['full_name']}", "success")

        try:
            fork_index = int(input("Select a fork to sync (enter number): ")) - 1
            fork = forks[fork_index]
            original = fork.get("parent", {}).get("full_name")
            if original:
                sync_branches(fork, original)
            else:
                write_output("Original repository not found.", "warning")
        except (ValueError, IndexError):
            write_output("Invalid selection.", "error")

    elif choice == "4":
        sync_all_forks()

    elif choice == "5":
        write_output("Exiting GitHub Fork Management.", "success")
        sys.exit()

    else:
        write_output("Invalid choice.", "error")

# Main execution
def main():
    while True:
        display_menu()
        handle_choice(input("Enter your choice: "))

if __name__ == "__main__":
    main()
