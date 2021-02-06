#!/bin/bash
cd /home/avnishnarayan
runuser -l avnishnarayan -c "git clone https://github.com/rlworkgroup/garage && cd garage/ && git checkout avnish-new-metaworld-results-st-v2 && mkdir data/"
runuser -l avnishnarayan -c "mkdir -p metaworld-runs-v2/local/experiment/"
runuser -l avnishnarayan -c "make run-headless -C ~/garage/"
runuser -l avnishnarayan -c "cd garage && python docker_metaworld_run_cpu.py 'metaworld_launchers/single_task_launchers/ppo_metaworld.py --env-name lever-pull-v2'"
runuser -l avnishnarayan -c "cd garage/metaworld_launchers && python upload_folders.py ppo 1200"
