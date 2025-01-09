#!/bin/bash

# Script makes a tarball with all accounting scripts
# When making a release put his tarball in the github repository releases
cd acc_scripts/
tar zcvf ../acc.tgz *.sh *.py
