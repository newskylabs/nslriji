#!/bin/sh
## =========================================================
## Boot script for the riji application.
## 
## This script is used from the Dockerfile to boot the
## riji Docker container. 
## ---------------------------------------------------------

# Activate the virtual Python environment
source venv/bin/activate

# Upgrade the database
while true; do

    # Upgrade the database though the migration framework
    flask db upgrade

    # Break from the loop when the update was successful
    if [[ "$?" == "0" ]]; then
        break
    fi

    # When database update failed print a message 
    # and try again after 5 seconds
    echo "Deploy command failed, retrying in 5 secs..."
    sleep 5

done

# Compile the language translations
flask translate compile

# Run the server with gunicorn.
# 
# The process running the script will be replaced by the gunicorn process:
# When this process terminates the Docker container does as well.
# 
# Docker appends anything that is written to stdout or stderr to the
# logs. Therefore gunicorn is configured to write access and error log
# messages to stdout via '--access-logfile -' and '--error-logfile -'.
# 
exec gunicorn -b :5000 --access-logfile - --error-logfile - riji:app

## =========================================================
## =========================================================

## fin.
