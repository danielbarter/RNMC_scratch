with (import /home/danielbarter/nixpkgs {});

pkgsStatic.nix.overrideAttrs (oldAttrs: rec {
  configureFlags = [ "--with-store-dir=/global/home/users/dbarter/.nix/store"
                     "--localstatedir=/global/home/users/dbarter/.nix/var"
                     "--sysconfdir=/global/home/users/dbarter/.nix/etc"
                     "--enable-gc"
                     "--disable-shared"
                     "--build=x86_64-unknown-linux-gnu"
                     "--host=x86_64-unknown-linux-musl" ];
    })
