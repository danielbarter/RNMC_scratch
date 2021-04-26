with (import <nixpkgs> {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "cb00eacac9874fd4314a623a8a9c1ac22d48efa5";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc sqlite];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "058m0s4mci7vbiqnfj3q33rw849shd53m051lz9cpiq4xmdfp6iz";
  };
  doCheck = true;
  mesonBuildType = "debug";
}
