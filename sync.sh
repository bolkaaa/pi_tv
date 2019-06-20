#!/bin/bash

if [ -e .uri ]; then
  REMOTE_URI=$(cat .uri)
  HOME_FOLDER="/home/pi/pi_tv"
  ACCOUNT_PATH=$(echo $REMOTE_URI | awk -F ":" '{print $2}')
  ACCOUNT_ID=$(echo $ACCOUNT_PATH | awk -F "media/" '{print $2}')
  LOG_FILE=$(echo $ACCOUNT_PATH | awk -F "/static" '{print $1}')/logs/${ACCOUNT_ID}.log
  SSH_ARGS="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
  # check for reboot request
  rsync --remove-source-files -avz -e "${SSH_ARGS}" ${REMOTE_URI}/tmp/.reboot ${HOME_FOLDER}/.reboot
  if [ -e ${HOME_FOLDER}/.reboot ]; then
  rm ${HOME_FOLDER}/.reboot
  sudo reboot
  fi
  #
  sudo youtube-dl -U
  rsync -avz -L -e "${SSH_ARGS}" ${REMOTE_URI}/uploads/ ${HOME_FOLDER}/media/
  rsync -avz -e "${SSH_ARGS}" --rsync-path="rm -f ${LOG_FILE} && rsync --log-file=${LOG_FILE}" ${REMOTE_URI}/playlist ${HOME_FOLDER}/playlist
fi
