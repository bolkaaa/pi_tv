#! /bin/bash
setterm -cursor off

MEDIA_FOLDER="<fill>"
PLAYLIST_FILE="${MEDIA_FOLDER}/playlist"

# infinite
while true; do
	if [ -e ${PLAYLIST_FILE} ]; then
		# loop playlist items
		cat ${PLAYLIST_FILE} | while read LINE
		do
			FILENAME=$(echo $LINE | cut -d'@' -f1)
			TYPE=$(echo $LINE | cut -d'@' -f2)
			DURATION=$(echo $LINE | cut -d'@' -f3)
			# make tty window nice & clean
			clear		
			DEST="${MEDIA_FOLDER}/uploads/${FILENAME}"
			# lets check if file exists
			if [ -e ${DEST} ]; then
				# lets run fbi if it is an image file...
				if [ "$TYPE" = "image" ]; then	
					fbi -d /dev/fb0 -a -t ${DURATION} -1 ${DEST} # >/dev/null 2>>/dev/null
					# else
					# vlc --play-and-exit -q $f	
				fi
			else
				sleep 1		
			fi
		done;
	else 
		sleep 1
	fi
done;
