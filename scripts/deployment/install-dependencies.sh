#!/bin/bash

# Get the directory where the script file is located
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [[ -f "$script_dir/../../.env" ]]; then
  ( set -a && source "$script_dir/../../.env" )
fi

# Get the current environment (converted to lowercase)
environment=$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')

if [ "$environment" != "local" ] && [ "$environment" != "production" ] && [ "$environment" != "development" ]; then
  echo "Invalid environment: $ENVIRONMENT"
  exit 1
fi

#Install external dependencies
pip install --upgrade pip
requirements_file="$script_dir/../../requirements.txt"
pip install -r "$requirements_file"
pip install gunicorn