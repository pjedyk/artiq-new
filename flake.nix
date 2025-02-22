{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-24.11";
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

        (pkgs.rust-bin.stable."1.75.0".default.override {
          extensions = ["rust-src"];
          targets = ["aarch64-unknown-none"];
        })
      ];
    };
  };
}
