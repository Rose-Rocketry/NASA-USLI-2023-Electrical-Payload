#!/run/current-system/sw/bin/bash
rsync --verbose --recursive ./*.py ./requirements.txt pi@rocket-pi:datalogger/
