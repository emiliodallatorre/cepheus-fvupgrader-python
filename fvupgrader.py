""" fvupgrader.py: A simple script to upgrade the version of a Flutter project. """

#!/usr/bin/env python3

import os.path
import re
from argparse import ArgumentParser
from pathlib import Path

from poetry.core.factory import Factory

version_regex: str = r"version: (\d+\.\d+\.\d+\+\d+)"
version_file: str = "pubspec.yaml"


class GitOperationException(Exception):
    """Exception raised for Git operation errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


def get_fvupgrader_version():
    """
    Get the version of the project from the pyproject.toml file.

    Returns:
        str: The version of the project.
    """
    pyproject_path = Path(__file__).parent / 'pyproject.toml'
    poetry = Factory().create_poetry(pyproject_path)

    return poetry.package.version


def get_version(directory_path: str) -> str:
    """
    Retrieves the version number from a file located in the specified directory.

    Args:
        directory_path (str): The path to the directory containing the version file.

    Returns:
        str: The version number extracted from the file.

    Raises:
        Exception: If the version number is not found in the file.
    """
    with open(f"{directory_path}/{version_file}", "r", encoding="utf-8") as file:
        content = file.read()
        match = re.search(version_regex, content)
        if match:
            return match.group(1)

        raise FileNotFoundError("Version not found in pubspec.yaml")


def get_available_next_versions(directory_path: str) -> list:
    """
    Returns a list of available next versions based on the current version of the directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        list[str]: A list of available next versions.
    """
    current_version = get_version(directory_path)
    current_version = current_version.replace("+", ".")
    major, minor, patch, build = current_version.split(".")
    return [
        f"{major}.{minor}.{int(patch) + 1}+{build}",
        f"{major}.{int(minor) + 1}.0+{build}",
        f"{int(major) + 1}.0.0+{build}",
    ]


def update_version(new_version: str, directory_path: str) -> None:
    """
    Update the version number in a file located at the specified directory path.

    Args:
        new_version (str): The new version number to update.
        directory_path (str): The path to the directory containing the version file.

    Returns:
        None
    """
    with open(f"{directory_path}/{version_file}", "r", encoding="utf-8") as file:
        content = file.read()
        new_content = re.sub(version_regex, f"version: {new_version}", content)
    with open(f"{directory_path}/{version_file}", "w", encoding="utf-8") as file:
        file.write(new_content)


def git_operations(new_version: str, directory_path: str, parsed_args) -> None:
    """
    Perform git operations such as committing changes, tagging releases, and pushing changes.

    Args:
        new_version (str): The new version to be used for the commit and tag.
        directory_path (str): The path to the directory where the git repository is located.
        parsed_args: The parsed command-line arguments.

    Returns:
        None
    """
    # Commit the changes
    if not parsed_args.no_commit:
        os.system(f"git -C {directory_path} add {version_file}")
        os.system(
            f"git -C {directory_path} commit -am 'Bump version to {new_version}'")

    # Tag the release
    if not parsed_args.no_tag:
        os.system(f"git -C {directory_path} tag {new_version}")
        print(f"Tagged release {new_version}")

    # Push the changes
    if not parsed_args.no_push:
        os.system(f"git -C {directory_path} push")


def is_dir_git_repo(directory_path: str) -> bool:
    """
    Check if a directory is a Git repository.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        bool: True if the directory is a Git repository, False otherwise.
    """
    return os.path.isdir(directory_path + "/.git")


def is_dir_flutter_project(directory_path: str) -> bool:
    """
    Check if the given directory contains a Flutter project.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        bool: True if the directory contains a Flutter project, False otherwise.
    """
    return os.path.isfile(directory_path + "/pubspec.yaml")


def main(parsed_args) -> None:
    """
    Main function for upgrading a Flutter project to a new version.

    Args:
        parsed_args: Parsed command-line arguments.

    Raises:
        FileNotFoundError: If the provided path is not a Flutter project.

    Returns:
        None
    """
    directory_path = os.path.abspath(parsed_args.path)

    if not is_dir_flutter_project(directory_path):
        raise FileNotFoundError("This is not a Flutter project")

    print("Current version:", get_version(directory_path))
    available_versions = get_available_next_versions(directory_path)

    if not parsed_args.major and not parsed_args.minor and not parsed_args.patch:
        print("Available next versions:")
        for index, version in enumerate(available_versions):
            print(f"{index + 1}. {version}")

        new_version_number = input("Choose a new version: ")
        new_version = available_versions[int(new_version_number) - 1]
    else:
        if parsed_args.major:
            new_version = available_versions[2]
        elif parsed_args.minor:
            new_version = available_versions[1]
        elif parsed_args.patch:
            new_version = available_versions[0]

    print(f"Updating to {new_version}...")

    update_version(new_version, directory_path)

    new_git_version: str = f"v{new_version}"
    if is_dir_git_repo(directory_path):
        git_operations(new_git_version, directory_path, parsed_args)


def fix_args(parsed_args) -> ArgumentParser:
    """
    Validates the command line arguments and raises exceptions if invalid combinations are detected.

    Args:
        args (ArgumentParser): The command line arguments.

    Raises:
        GitOperationException: If the combination of arguments is invalid.

    Returns:
        ArgumentParser: The validated command line arguments.
    """
    if not parsed_args.no_push and parsed_args.no_commit:
        raise GitOperationException("You cannot push without committing")
    if not parsed_args.no_tag and parsed_args.no_commit:
        raise GitOperationException("You cannot tag without committing")

    if parsed_args.major and parsed_args.minor:
        raise GitOperationException(
            "You cannot upgrade the major and minor versions at the same time")
    if parsed_args.major and parsed_args.patch:
        raise GitOperationException(
            "You cannot upgrade the major and patch versions at the same time")
    if parsed_args.minor and parsed_args.patch:
        raise GitOperationException(
            "You cannot upgrade the minor and patch versions at the same time")

    return parsed_args


def entry_point() -> None:
    """
    Entry point function for the fvupgrader script.

    Parses command line arguments, fixes the arguments, and calls the main function.
    """
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--path", help="path to the directory containing the pubspec.yaml file",
        type=str, default=".", required=False
    )
    parser.add_argument(
        "--no-push", help="push the changes to the git repository",
        action="store_true", default=False
    )
    parser.add_argument(
        "--no-commit", help="commit the changes to the git repository",
        action="store_true", default=False
    )
    parser.add_argument(
        "--no-tag", help="tag the release in the git repository",
        action="store_true", default=False
    )
    parser.add_argument(
        "--major", help="upgrade the major version",
        action="store_true", default=False
    )
    parser.add_argument(
        "--minor", help="upgrade the minor version",
        action="store_true", default=False
    )
    parser.add_argument(
        "--patch", help="upgrade the patch version",
        action="store_true", default=False
    )
    parser.add_argument(
        "--version",
        action="version", version=f"%(prog)s v{get_fvupgrader_version()}"
    )

    args = parser.parse_args()
    args = fix_args(args)

    main(args)


if __name__ == "__main__":
    entry_point()
