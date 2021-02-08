with (import /home/danielbarter/nixpkgs {});

let pythonEnv = python38.withPackages (
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
