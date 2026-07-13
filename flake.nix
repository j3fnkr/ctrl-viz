{
  description = "python pkgs for ctrl-viz";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
  # get system specific os info
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        ctrlViz = python.pkgs.buildPythonPackage rec {
          pname = "ctrl-viz";
          pyproject = true;
          build-system = [pkgs.python312Packages.setuptools];
          version = "0.1.1";
          src = ./.; # Path to your package (where setup.py is)
          propagatedBuildInputs = with python.pkgs; [
            # List your Python dependencies here, e.g.:
            numpy
            scipy
            matplotlib
            control
          ];
          doCheck = false; # Skip tests for editable installs
        };
      in {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            export PYTHONPATH="$PWD/src''${PYTHONPATH:+:$PYTHONPATH}"
          '';
          packages = [
            (pkgs.python312.withPackages (ps:
              with ps; [
                numpy
                jupyter
                jupyterlab-vim
                scipy
                matplotlib
                dash
                plotly
                dash-bootstrap-components
                control
              ]))
            ctrlViz
          ];
        };
      }
    );
}
