#!/bin/bash
cd ../
rm -rf rust
rm -rf target
rm -rf .git
rm CrowdMaster-logo.gif
cd ../
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
  zip -r CrowdMaster_macOS_Auto.zip CrowdMaster
  curl --ftp-create-dirs -T CrowdMaster_macOS_Auto.zip -u $FTP_USER:$FTP_PASSWORD ftp://jmroper.com/public_html/crowdmaster-builds/
fi
if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then 
  zip -r CrowdMaster_Linux_Auto.zip CrowdMaster
  curl --ftp-create-dirs -T CrowdMaster_Linux_Auto.zip -u $FTP_USER:$FTP_PASSWORD ftp://jmroper.com/public_html/crowdmaster-builds/
fi