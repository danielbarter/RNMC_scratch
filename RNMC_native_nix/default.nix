with (import /home/danielbarter/nixpkgs {});

stdenv.mkDerivation rec {
  name = "RNMC_native";
  hash = "2734f5de80a9610adc583b0b14bc7a36234ba287";
  buildInputs = [gcc gsl zip];
  src = fetchurl {
    url = "https://github.com/danielbarter/RNMC_native/archive/${hash}.tar.gz";
    sha256 = "0ddn12brw97h4s8qs0wnsabnqs3qv5afmz3ysq1xbsf6z30q1c8m";
  };

  builder = ./builder.sh;
}
