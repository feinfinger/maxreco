WDIR=$PWD
git clone http://github.com/tomopy/tomopy
cd $WDIR/tomopy
python setup.py install
cd $WDIR
git clone http://github.com/feinfinger/p05tools
git clone https://github.com/hgomersall/pyFFTW.git pyfftw
cd $WDIR/pyfftw 
python setup.py build_ext --inplace
cd $WDIR
git clone http://github.com/blink1073/tifffile
git clone http://github.com/PyWavelets/pywt
git clone http://github.com/data-exchange/DXchange dxchange
echo 'TOMPY INSTALLATION DONE.'
