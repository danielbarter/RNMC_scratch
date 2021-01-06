source $stdenv/setup
mkdir $out
tar xvfz $src
cd openbabel-*
mkdir ob-build
cd ob-build
cmake -DRUN_SWIG=ON -DPYTHON_BINDINGS=ON -DCMAKE_INSTALL_PREFIX=$out -DLIB_INSTALL_DIR=$out  ..
make -j$NIX_BUILD_CORES install
patchelf --add-needed $out/libopenbabel.so.7 $out/lib/python3.8/site-packages/openbabel/_openbabel.so

setup_file="
from distutils.core import setup

setup(
    name = 'pyopenbabel',
    version = '3.1.1',
    packages = ['openbabel'],
    package_data = {'openbabel' : ['_openbabel.so']}
    )
"


echo "$setup_file" > $out/lib/python3.8/site-packages/setup.py
