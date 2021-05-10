with (import /home/danielbarter/nixpkgs  {});


let
  python = let
    packageOverrides = self: super: {



      pymatgen = super.pymatgen.overridePythonAttrs (
        old: { version = "2022.0.6";
               src = super.fetchPypi {
                 pname = "pymatgen";
                 version = "2022.0.4";
                 extension = "tar.gz";
                 sha256 = "0x05glcgczyjrmfrigsrm6nb7d9whfk6ilralqwn17hp2264jhbj";};
               checkInputs = [ super.pytest ];
             }
      );


    }; in python38.override {inherit packageOverrides;};

  pythonEnv = python.withPackages (
      ps: [ ps.pymatgen
            ps.numpy
            ps.monty
            ps.openbabel-bindings
            ps.networkx
            ps.pygraphviz
            ps.pytest
            ps.numba
            ps.black
            ps.pycodestyle
            ps.flake8
            ps.mypy
            ps.pulp
          ]);
in mkShell rec {
  buildInputs = [ pythonEnv
                  graphviz
                  texlive.combined.scheme-small
                  sqlitebrowser
                  cbc
                  (import ./RNMC_native)
                ];
}
