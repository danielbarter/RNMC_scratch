with (import <nixpkgs> {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "455653a2a3de7d45d8410e6b340df33005169d40";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "0kb0bg3qfzbm0zzxdl9rv8lb8kj28r3mz5a9f16kf0k9px8w9kws";
  };
  doCheck = true;
  mesonBuildType = "debug";
}
