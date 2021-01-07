with (import <nixpkgs> {});

pkgsStatic.nix.overrideAttrs (oldAttrs: rec {
  configureFlags = [ "--with-store-dir=/global/home/users/dbarter/.nix/store"
                     "--localstatedir=/global/home/users/dbarter/.nix/var"
                     "--sysconfdir=/global/home/users/dbarter/.nix/etc"
                     "--with-sandbox-shell=/global/home/users/dbarter/sh"
                     "--disable-init-state"
                     "--enable-gc"
                     "--disable-shared"
                     "--enable-static"
                     "--build=x86_64-unknown-linux-gnu"
                     "--host=x86_64-unknown-linux-musl" ];
    })
