with (import <nixpkgs> {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "f27d29f92d36aed476bb9e2507d3215e5e69b85d";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc sqlite];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "1zfr3h7m5s0bix42p2q4d6k3xyzkylcl317hx07kbc2bs5h0b0xc";
  };
  doCheck = true;
  mesonBuildType = "debug";
}
