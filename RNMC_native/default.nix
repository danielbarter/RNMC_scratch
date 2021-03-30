with (import <nixpkgs> {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "f5ac3d79296fc3874fc6e2b6a3a85dce6cbc7434";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "17k0sh5kq8f2fm4gv8hgn1z2dcr70f4w2zw56ph9rpcxx6jlp647";
  };
  doCheck = true;
  mesonBuildType = "debug";
}
