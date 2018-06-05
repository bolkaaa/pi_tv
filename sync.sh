#!/bin/bash

if [ -e .uri ]; then
  REMOTE_URI=$(cat .uri)
  HOME_FOLDER="/home/pi/pi_tv"
  SSH_ARGS="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
  rsync -avz -L -e "${SSH_ARGS}" ${REMOTE_URI}/uploads/ ${HOME_FOLDER}/media/
  rsync -avz -e "${SSH_ARGS}" ${REMOTE_URI}/playlist ${HOME_FOLDER}/playlist
fi