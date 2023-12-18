# Raspberry PI Slideshow Christmas Ornament

This project is designed for a PI Zero 2W to be connected to a 3.5" TFT screen that can then be hung on a Christmas tree. It displays a slideshow of images on the screen, showing each for a configurable duration.

## Install

* Install Raspberry PI OS on the PI
* Attach the 3.5" screen
* Follow the manufacturers instructions to set up the screen
* Reboot
* Install docker, docker.io and docker-compose via:
```
sudo apt install -y docker docker.io docker-compose
```
* Open a browser and navigate to https://github.com/jeffspiinthesky/slideshow
* Drop down the 'Code' button and select 'Download ZIP'
* Transfer the ZIP file to your Raspberry PI
* Unzip the file
```
unzip slideshow-main.zip
```
* Change to the extracted directory
```
cd slideshow-main
```
* Build the containers
```
docker build --rm -t jeffspiinthesky/slideshow:0.0.1 -f Dockerfile-flask .
docker build --rm -t jeffspiinthesky/slideshowclient:0.0.1 -f Dockerfile-client .
```

## Start the application
```
docker-compose -f docker-compose.yml up -d
```