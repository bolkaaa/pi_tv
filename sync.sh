#!/bin/bash

HASH_STRING="<fill>"

PI_TV_SERVER="<fill>"
REMOTE_MEDIA_FOLDER="/home/pi_tv/pi_tv-server/app/static/media/${HASH_STRING}"
HOME_FOLDER="/home/pi/pi_tv"

rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" pi_tv@${PI_TV_SERVER}:${REMOTE_MEDIA_FOLDER}/uploads/ ${HOME_FOLDER}/media/
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" pi_tv@${PI_TV_SERVER}:${REMOTE_MEDIA_FOLDER}/playlist ${HOME_FOLDER}/playlist
