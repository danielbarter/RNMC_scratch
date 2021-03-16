source $stdenv/setup

tar xvfz $src
cd "RNMC_native-$hash"
./build.sh RNMC
mkdir $out
cp ./bin/RNMC $out
