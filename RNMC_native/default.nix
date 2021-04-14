with (import <nixpkgs> {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "e05e265dc79e34baa28c472ec35825e2dfa388d0";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc sqlite];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "097gaw0w4rmpafndfixyb9nfxhr9mg2k57yd0h0ic4jnm9n05r6j";
  };
  doCheck = true;
  mesonBuildType = "debug";
}
