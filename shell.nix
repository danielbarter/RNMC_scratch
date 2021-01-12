with (import ../hpc-nix/nixpkgs {});


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
