#!/bin/bash

# create diretories
WDIR=$PWD

# tomopy
cd $WDIR
git clone http://github.com/tomopy/tomopy
cd $WDIR/tomopy
python setup.py build

# scikit-image
cd $WDIR
git clone https://github.com/scikit-image/scikit-image.git
cd $WDIR/scikit-image
python setup.py build
cp -r scimage $WDIR

# p05tools
cd $WDIR
git clone http://github.com/feinfinger/p05tools.git

# pyfftw
cd $WDIR
git clone https://github.com/hgomersall/pyFFTW.git pyfftw
cd $WDIR/pyfftw 
python setup.py build_ext --inplace

# tifffile
cd $WDIR
git clone http://github.com/blink1073/tifffile
cd $WDIR/tifffile
python setup.py build

# pywt
cd $WDIR
git clone http://github.com/PyWavelets/pywt
cd $WDIR/pywt
python setup.py build

# dxchange
git clone http://github.com/data-exchange/DXchange dxchange_repo
cd $WDIR/dxchange_repo
python setup.py build
cp -r dxchange $WDIR

# make files/dirs writeable
cd $WDIR
find $WDIR -type d -exec chmod 750 {} \;
find $WDIR -type f -exec chmod 660 {} \;

# finish
echo 'TOMOPY INSTALLATION DONE.'
