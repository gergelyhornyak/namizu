#!/bin/bash

# Start timing Command 1
start1=$(date +%s.%N)
sudo docker compose build
end1=$(date +%s.%N)
duration1=$(echo "$end1 - $start1" | bc)

start2=$(date +%s.%N)
sudo docker compose down && sudo docker compose up -d
end2=$(date +%s.%N)
duration2=$(echo "$end2 - $start2" | bc)

# Add total duration
total=$(echo "$duration1 + $duration2" | bc)

echo "Total container build time: $total seconds"

