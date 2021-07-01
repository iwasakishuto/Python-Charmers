#!/bin/bash
PLATFORM=$1

if [[ "${PLATFORM}" == macos* ]]
then
    brew update && brew upgrade brew-cask && brew cleanup && brew cask cleanup
    brew install homebrew/cask/wkhtmltopdf
    # brew install gcc
else 
    # sudo apt-get clean && sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get dist-upgrade
    # sudo apt-get update --allow-releaseinfo-change
    sudo apt-get install xvfb libfontconfig wkhtmltopdf
    sudo apt-get install -y cmake gcc g++
fi