#! /bin/bash

git fetch --all
git reset --hard origin/master
git pull origin master

exit 0

setterm -term linux -background black -foreground black -cursor off

cleanup ()
{
killall fbi
killall omxplayer	
kill -s SIGTERM $!
setterm -term linux -background black -foreground white -cursor on	
exit 0
}

trap cleanup SIGINT SIGTERM

PI_TV_FOLDER="/home/pi/pi_tv"
MEDIA_FOLDER="${PI_TV_FOLDER}/media"
PLAYLIST_FILE="${PI_TV_FOLDER}/playlist"
VIDEO_RECOVER=3

while true; 
do	
if [ -e ${PLAYLIST_FILE} ]; then
cat ${PLAYLIST_FILE} | while read LINE
do {
FILENAME=$(echo $LINE | cut -d'@' -f1)
TYPE=$(echo $LINE | cut -d'@' -f2)
DURATION=$(echo $LINE | cut -d'@' -f3)
clear		
DEST="${MEDIA_FOLDER}/${FILENAME}"
if [[ ( -e ${DEST} ) || ( "$TYPE" = "url" ) ]]; then
if [ "$TYPE" = "image" ]
then	
	fbi -d /dev/fb0 -T 1 --noverbose --nocomments -a -t $DURATION -1 ${DEST} > /dev/null 2>>/dev/null	
elif [ "$TYPE" = "video" ]
then	
	omxplayer -o hdmi -r ${DEST} > /dev/null 2>>/dev/null
	sleep $VIDEO_RECOVER
elif [ "$TYPE" = "url" ]
then	
	VURL=$(youtube-dl -g ${FILENAME} -f best)
	omxplayer -o hdmi -r $VURL --live > /dev/null 2>>/dev/null
	sleep $VIDEO_RECOVER
else
	sleep 0	
fi
# wait the running processes to finish and move on
while ps ax | grep -v grep | grep -E "omxplayer|fbi" > /dev/null; do
	sleep 0.1
done;
else
sleep 1		
fi
} < /dev/null; 
done;
else 
sleep 1
fi	
wait $!	
done
