#!/bin/bash

#sudo fbi -T 2 -d /dev/fb0 -noverbose -a /mnt/src/dragdropupload/uploads/bg.jpg

IMAGE_DIR=/images

# Test connectivity to web services and loop till they're available
BROKEN=1
while [[ ${BROKEN} -eq 1 ]]
do
	curl -s http://slideshow:5000/getduration
	if [[ $? -eq 0 ]]
	then
		echo "Web services working"
		break
	else
		echo "Cannot call web services. Retrying in 5s..."
		sleep 5
	fi
done

CHANGE=1
DURATION=$(curl -s http://slideshow:5000/getduration | jq ".[0]" )

while [ 1==1 ]
do
	if [[ ${CHANGE/$'\r'/} -eq 1 ]]
	then
	        # Get list of images
       		curl -s http://slideshow:5000/pictures | jq ".[][1]" | sed 's/"//g' > /tmp/files.txt
        	# Get duration from DB
        	DURATION=$(curl -s http://slideshow:5000/getduration | jq ".[0]")

		# Clear change flag
		curl http://slideshow:5000/clearchange
	fi
	# loop round images
	while read IMAGE 
	do
		echo "Displaying image ${IMAGE_DIR}/${IMAGE}"
		fbi -T 2 -d /dev/fb0 -noverbose -a ${IMAGE_DIR}/${IMAGE}
		sleep ${DURATION}
		# get change flag
		CHANGE=$(curl -s http://slideshow:5000/getchange | jq ".[0]")
		if [[ ${CHANGE} -eq 0 ]]
		then
			echo "No change"
		else
			echo "Changed - Abort!!"
			break;
		fi
	done < /tmp/files.txt	
done
