# Traffic scene renderer

This traffic scene renderer enables drawing top-view overviews of traffic constellations. 
This drawings can be printed on screen using `matplotlib` and exported to images or `tikz` files that can be rendered with LaTeX to create vector-based drawings of the traffic scenes.

## Installation

Installation can be done using `pip`. Simply run

    pip install traffic-scene-renderer

## Usage


## Development

Yes, you can help! Follow the steps below to contribute to this package:

1. Download the git repository, e.g., using `git clone git@github.com:ErwindeGelder/TrafficSceneRenderer.git`
2. Create a virtual environment, e.g., using `python -m venv venv`
3. Activate the virtual environment (e.g., on Windows, `venv\Scripts\activate.bat`)
4. Install the necessary libraries using `pip install -e .[dev]`
5. The `main` branch is protected, meaning that you cannot directly push changes to this branch. 
   Therefore, if you want to make changes, do so in a seperate branch. 
   For example, you can create a new branch using `git checkout -b feature/my_awesome_new_feature`.
6. Before pushing changes, ensure that the code adheres to the linting rules and that the tests are successful.
   To run the linting and testing, `tox` first needs to know where it can find the different Python versions that are supported.
   One way to do so is by making use of `pyenv` or [pyenv-win](https://github.com/pyenv-win/pyenv-win).
   Note that you only need to do this once for a single machine.
7. Run `tox run -e lint`. If issues arise, fix them. You can do the linting commands manually using:
   1. `ruff format . --check` (remove the `--check` flag to let `ruff` do the formatting)
   2. `ruff check .`
   3. `mypy .`
8. Run `tox run -f test`
9. Check if the tests covered everything using the coverage report in `/reports/coverage_html/index.html`
10. Push changes to GitHub. If everything is OK and you want to merge your changes to the `main` branch, create a pull request.
   Ideally, there is at least one reviewer who reviews the pull request before the merge.
