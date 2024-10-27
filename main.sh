#!/bin/bash

# Remote server details
remote_host="" # Change this value for each remote server
remote_username="" # Change this value for each remote server
remote_password="" # Change this value for each remote server
remote_folder_location="" # Change this value for each remote server
local_log_file="debug.log"

# Array of coin names and corresponding screen names
# These coin names stay the same across all stratum servers
# Only Master Daemon will have more coins in there than this script
screen_names=("Alephium" "Brics" ) # Add more coin names here
coin_names=("alph_pplns" "brics_pplns" ) # Corresponding screen names / coin id names 

# Use sshpass to connect to the remote server and execute the entire script remotely for each coin
for ((i=0; i<${#screen_names[@]}; i++)); do
  coin_name="${coin_names[i]}"
  screen_name="${screen_names[i]}"

  # Combine remote folder location and screen name
  full_screen_name="$remote_folder_location-$screen_name"

  # Path to the log file on the remote server
  remote_log_file="/path-to-directory/.$coin_name/$local_log_file"

  # Set up local log file location for the current coin
  local_log_file_location="/path-to-directory/$remote_folder_location/debug/$screen_name/$local_log_file"

  # Start a screen session remotely for each coin
  screen -dmS "$full_screen_name" bash -c "sshpass -p '$remote_password' ssh -o StrictHostKeyChecking=no $remote_username@$remote_host 'tail -f $remote_log_file'"

  # Wait for a few seconds to allow screen to start capturing the output
  sleep 5

  # Attach to the screen session and set up local log file location
  screen -x "$full_screen_name" -X logfile "$local_log_file_location"
  screen -x "$full_screen_name" -X log
done
