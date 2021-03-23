with (import /home/danielbarter/nixpkgs {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "2d29393f13944e829e55cc7968eb5e600d6356fd";
  buildInputs = [gsl];
  nativeBuildInputs = [meson ninja gcc];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "1jgp7h8xh6rmdaw63bv8s9gk3jph9p8aj2ikhp72hhxypblnrmma";
  };
  doCheck = true;
}
