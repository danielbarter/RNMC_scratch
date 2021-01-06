{stdenv, fetchurl, fetchpatch, cmake, zlib, libxml2, eigen, python, cairo, pcre, pkgconfig, swig, rapidjson }:

stdenv.mkDerivation rec {
  pname = "openbabel3";
  version = "3.1.1";

  src = fetchurl {
    url = "https://github.com/openbabel/openbabel/archive/openbabel-3-1-1.tar.gz";
    sha256 = "c97023ac6300d26176c97d4ef39957f06e68848d64f1a04b0b284ccff2744f02";
  };


  buildInputs = [ zlib libxml2 eigen python cairo pcre swig rapidjson];

  nativeBuildInputs = [ cmake pkgconfig ];

  builder = ./openbabel3_builder.sh;

  meta = {
    description = "A toolbox designed to speak the many languages of chemical data";
    homepage = "http://openbabel.org";
    platforms = stdenv.lib.platforms.all;
    license = stdenv.lib.licenses.gpl2Plus;
  };
}
