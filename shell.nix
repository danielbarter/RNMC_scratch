# using this particular commit because openblas is version 0.3.12
# 23b939cfc336612fc7c5ba6213aea7966c872153
with (import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23b939cfc336612fc7c5ba6213aea7966c872153.tar.gz") {});


let
  python = let
    packageOverrides = self: super: {
      numpy = super.numpy.overridePythonAttrs (
        old: { version = "1.19.2";
               src = super.fetchPypi {
                 pname = "numpy";
                 version = "1.19.2";
                 extension = "zip";
                 sha256 = "0k28m123rc0jy9srg6f9wk80bdwpc5rxwzddcmq554z7w4q0fc8d";};
               checkInputs = [ super.hypothesis ];
             }
      );

      networkx = super.networkx.overridePythonAttrs (
        old: { version = "2.5";
               src = super.fetchPypi {
                 pname = "networkx";
                 version = "2.5";
                 sha256 = "00hnii2lplig2s324k1hvi29pyfab6z7i22922f67jgv4da9ay3r";};
             }
      );

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
          ps.scipy
          ps.sympy
          ps.networkx
          ps.numba
          ps.matplotlib
          ps.jupyterlab
          ps.cython
          ps.pre-commit
          ps.pytest
          ps.pycodestyle
          ps.pydocstyle
          ps.flake8
          ps.mypy
          ps.mypy-extensions
          ps.pyarrow
          ps.pyopenbabel
        ]);

in mkShell rec {

  BABEL_LIBDIR = "${openbabel}/openbabel/3.1.0";
  LD_LIBRARY_PATH = openbabel;


  # make sure that CPATH contains all the correct headers
  CPATH = lib.concatStringsSep ":" [( lib.makeSearchPathOutput "dev" "include" [flint clang glibc gmp mpfr] )
                                   ( lib.makeSearchPathOutput "dev" "include/python3.8" [pythonEnv])];
  buildInputs = [ pythonEnv
                  arrow-cpp
                  openbabel
                  flint
                  gcc
                  glibc
                  gmp  # flint dependency
                  mpfr # flint dependency
                ]; }
