#!/bin/bash
# ref: https://github.com/nanasess/setup-chromedriver
PLATFORM=$1
CHROMEVERSION=$2

# <--- Set Environment Variables. ---
if [[ "${PLATFORM}" == macos* ]]
then
    ARCHITECTURE="mac64"
    export DISPLAY=:99
else 
    ARCHITECTURE="linux64"
    export DISPLAY=:0
    sudo apt-get install -y \
      xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
      libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 \
      libxcb-xtest0-dev libxcb-shape0-dev libxcb-xkb-dev
fi
# --- Set Environment Variables. --->

# <--- Download chromedriver ---
wget -c -nc --retry-connrefused --tries=0 "https://chromedriver.storage.googleapis.com/${CHROMEVERSION}/chromedriver_${ARCHITECTURE}.zip"
unzip -o -q "chromedriver_${ARCHITECTURE}.zip"
sudo mv chromedriver /usr/local/bin/chromedriver
rm "chromedriver_${ARCHITECTURE}.zip"
# --- Download chromedriver --->

# <--- set up chromedriver ---
chromedriver --url-base=/wd/hub &
sudo Xvfb -ac $DISPLAY -screen 0 1280x1024x24 > /dev/null 2>&1 &    
# --- set up chromedriver ---