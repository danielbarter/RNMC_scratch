source $stdenv/setup

tar xvfz $src
cd "RNMC_native-$hash"
./build.sh RNMC
mkdir $out
mkdir $out/bin
cp ./bin/RNMC $out/bin
