WDIR=$PWD
git clone http://github.com/tomopy/tomopy
cd $WDIR/tomopy
python setup.py build
cd $WDIR
git clone https://github.com/scikit-image/scikit-image.git
cd $WDIR/scikit-image
python setup.py build
git clone http://github.com/feinfinger/p05tools.git
git clone https://github.com/hgomersall/pyFFTW.git pyfftw
cd $WDIR/pyfftw 
python setup.py build_ext --inplace
cd $WDIR
git clone http://github.com/blink1073/tifffile
cd $WDIR/tifffile
python setup.py build
cd $WDIR
git clone http://github.com/PyWavelets/pywt
git clone http://github.com/data-exchange/DXchange dxchange
cd $WDIR/dxchange
python setup.py build
cd $WDIR
find $WDIR -type d -exec chmod 750 {} \;
find $WDIR -type f -exec chmod 660 {} \;
echo 'TOMOPY INSTALLATION DONE.'
