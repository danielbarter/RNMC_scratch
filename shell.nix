# using this particular commit because openblas is version 0.3.12
# 23b939cfc336612fc7c5ba6213aea7966c872153
with (import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23b939cfc336612fc7c5ba6213aea7966c872153.tar.gz") {});


let
  python = let
    packageOverrides = self: super: {
      pyarrow = super.pyarrow.overridePythonAttrs (
        old: { PYARROW_WITH_PLASMA = true;}
      );

      pyopenbabel = super.buildPythonPackage {
        pname = "openbabel";
        version = "3.1.1";
        src = "${openbabel}/lib/python3.8/site-packages";
        # these env variables are used to locate various shared objects
        # see https://openbabel.org/docs/dev/Installation/install.html
        BABEL_LIBDIR = "${openbabel}/openbabel/3.1.0";
        LD_LIBRARY_PATH = openbabel;

      };


    }; in python38.override {inherit packageOverrides;};

  openbabel3 = (import ./openbabel3.nix);
  openbabel = (callPackage openbabel3 {python = python;});

  pythonEnv = python.withPackages (
    ps: [ ps.pymatgen
          ps.numpy
          ps.networkx
          ps.matplotlib
          ps.jupyterlab
          ps.pyarrow
          ps.pyopenbabel
        ]);

in mkShell rec {

  BABEL_LIBDIR = "${openbabel}/openbabel/3.1.0";
  LD_LIBRARY_PATH = openbabel;

  buildInputs = [ pythonEnv
                  arrow-cpp
                  openbabel
                ]; }
