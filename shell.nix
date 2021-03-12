with (import /home/danielbarter/nixpkgs {});


let
  python = let
    packageOverrides = self: super: {



      pymatgen = super.pymatgen.overridePythonAttrs (
        old: { version = "2022.0.4";
               src = super.fetchPypi {
                 pname = "pymatgen";
                 version = "2022.0.4";
                 extension = "tar.gz";
                 sha256 = "0x05glcgczyjrmfrigsrm6nb7d9whfk6ilralqwn17hp2264jhbj";};
               checkInputs = [ super.pytest ];
             }
      );

      numpy = super.numpy.overridePythonAttrs (
        old: { version = "1.20.1";
               src = super.fetchPypi {
                 pname = "numpy";
                 version = "1.20.1";
                 extension = "zip";
                 sha256 = "02m6sms6wb4flfg8y4h0msan4y7w7qgfqxhdk21lcabhm2339iiv";};
               checkInputs = [ super.hypothesis super.pytest ];
               patches = [];
             }
      );

      pandas = super.pandas.overridePythonAttrs (
        old: {
          disabledTests = old.disabledTests ++ ["test_loc_setitem_empty_append_raises"];
        }
      );


    }; in python38.override {inherit packageOverrides;};

  pythonEnv = python.withPackages (
      ps: [ ps.pymatgen
            ps.numpy
            ps.openbabel-bindings
            ps.networkx
            ps.pygraphviz
          ]);
in mkShell rec {
  buildInputs = [ pythonEnv
                  graphviz
                  texlive.combined.scheme-small
                ];
}
