#!/usr/bin/env bash

usage() {
  echo "[*] Usage: $(basename $0) [workspace name]"
}

## Start of the script
workspace_link="~/audit"
workspaces_dir="~/Documents/1_audits"

# Ensure the workspace name is submitted
if [ -z "$1" ]; then
  usage
  exit 1
fi
workspace_path="${workspaces_dir}/$1"

# Check no workspace link already exists
if [ -L "${workspace_link}" ]; then
  echo "[-] $workspace_link already exists"
  echo "[+] Please delete it and create a new one: rm ${workspace_link} && ln -s ${workspace_path} ${workspace_link}"
  exit 1
fi

# If desired workspace already exist, exit
if [ -d "${workspace_path}" ]; then
  echo "[-] $workspace_path already exists"
  exit 1
else
  echo "[*] Creating new workspace '${workspace_path}'"
  mkdir "${workspace_path}" 
  mkdir "${workspace_path}/"{gestion,rapports,data,notes}
  echo "[*] Linking workspace to ${workspace_link}"
  ln -s "${workspace_path}" ~/audit
fi
