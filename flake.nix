{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.05";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    rust-overlay,
  }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      overlays = [(import rust-overlay)];
    };
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        pkgs.alejandra
        pkgs.clang-tools

        (pkgs.python3.withPackages (ps: [
          ps.isort
          ps.black
          ps.pylint
          ps.mypy
          ps.colorama
          ps.pyyaml
        ]))

        (pkgs.rust-bin.stable."1.84.0".default.override {
          extensions = ["rust-src"];
          targets = ["armv7r-none-eabihf"];
        })
      ];
      env = {
        LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
        BB_ENV_PASSTHROUGH_ADDITIONS = "LOCALE_ARCHIVE";
      };
    };
  };
}
