# Traffic scene renderer

This traffic scene renderer enables drawing top-view overviews of traffic constellations. 
This drawings can be printed on screen using `matplotlib` and exported to images or `tikz` files that can be rendered with LaTeX to create vector-based drawings of the traffic scenes.

## Installation

Installation can be done using `pip`. Simply run

    pip install traffic-scene-renderer

## Usage


## Development

Yes, you can help! Follow the steps below to contribute to this package:

1. Download the git repository, e.g., using
   `git clone git@github.com:ErwindeGelder/TrafficSceneRenderer.git`.
2. Create a virtual environment, e.g., using `python -m venv venv`.
3. Activate the virtual environment (e.g., on Windows, `venv\Scripts\activate`).
4. Install `uv` using `pip install uv` and then `tox-uv` using `uv pip install tox-uv`.
5. The main branch is protected, meaning that you cannot directly push changes to this branch. 
   Therefore, if you want to make changes, do so in a seperate branch. For example, you can create 
   a new branch using `git checkout -b feature/my_awesome_new_feature`.
6. Before pushing changes, ensure that the code adheres to the linting rules and that the tests are 
   successful. Run `tox`. This does a linting check and runs all test scripts. To manually perform 
   these steps, use the following commands:
   1. Run `tox -e lint`. You can do the linting commands manually using:
      1. (One time) `uv pip install -r requirements-lint.txt`
      2. `ruff format . --check` (remove the `--check` flag to let `ruff` do the formatting)
      3. `ruff check .`
      4. `mypy .`
   2. Run `tox -e py310`.
   3. Run `tox -e py311`.
   4. Run `tox -e py312`.
   5. Run `tox -e py313`.
   6. Run `tox -e py314`.
   7. Run `tox -e combine-test-reports`
7. Check if the tests covered everything using the coverage report in 
   `/reports/coverage_html/index.html`.

   NOTE: Currently, not all code is covered. Ideally, all code is covered, but for now, ensure that 
   all *new* code is covered by the testing.
8. Push changes to GitHub. If everything is OK and you want to merge your changes to the `main`
   branch, create a pull request.
   Ideally, there is at least one reviewer who reviews the pull request before the merge.

Note that currently only "Code owners" can merge pull requests onto the `main` branch. This is to
ensure that not everyone can break the main code (even unintentially). If you want to be a "Code
owner", let us know!
