wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.46.tar.gz
tar zxvf bcm2835-1.46.tar.gz
cd bcm2835-1.46
./configure
make
sudo make check
sudo make install
nmp install 

# Run with sudo 
# https://www.hackster.io/vshymanskyy/raspberry-pi-node-js-blynk-app-dht11-dht22-am2302-c356a8
