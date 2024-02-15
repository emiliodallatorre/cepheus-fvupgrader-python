# Flutter Version Upgrader (fvupgrader)

[![Pylint](https://github.com/emiliodallatorre/fvupgrader/actions/workflows/pylint.yml/badge.svg)](https://github.com/emiliodallatorre/fvupgrader/actions/workflows/pylint.yml)
[![Upload Python Package](https://github.com/emiliodallatorre/fvupgrader/actions/workflows/python-publish.yml/badge.svg)](https://github.com/emiliodallatorre/fvupgrader/actions/workflows/python-publish.yml)
[![PyPI version](https://badge.fury.io/py/fvupgrader.svg)](https://badge.fury.io/py/fvupgrader)

This is a Python script that automates the process of upgrading the version of a Flutter project. It updates the version in the `pubspec.yaml` file, commits the changes, tags the release, and pushes the changes to the remote repository.

## Features

- Automatically increments the major, minor, or patch version of your Flutter project.
- Commits the version change to your Git repository.
- Tags the new version in your Git repository.
- Pushes the changes to your remote Git repository.

## Usage

1. Ensure you have Python 3 installed on your machine.
2. Clone this repository or download the `fvupgrader.py` file.
3. Navigate to the directory containing the `fvupgrader.py` file in your terminal.
4. Run the script with the `--path` argument pointing to your Flutter project:

```bash
python fvupgrader.py --path /path/to/flutter/project
```

Replace `/path/to/flutter/project` with the actual path to your Flutter project. If you don't provide the `--path` argument, the script will use the current directory (`.`) as the default.

## Installation

You can download the `fvupgrader.py` script directly from the repository:

```bash
curl -O https://raw.githubusercontent.com/emiliodallatorre/cepheus-fvupgrader-python/main/fvupgrader.py
```

To install it, move the downloaded script to /usr/local/bin:

```bash
sudo mv fvupgrader.py /usr/local/bin/fvupgrader
```

After moving the script, you can run it from anywhere on your system by typing `fvupgrader` in your terminal.

## Requirements

- Python 3
- Git

## Note

This script assumes that your Flutter project's version follows the pattern `major.minor.patch+build` in the `pubspec.yaml` file.
