#!/usr/bin/env python3

import os.path
import re
from argparse import ArgumentParser

version_regex: str = r"version: (\d+\.\d+\.\d+\+\d+)"
version_file: str = "pubspec.yaml"


def get_version(directory_path: str) -> str:
    with open(f"{directory_path}/{version_file}", "r") as file:
        content = file.read()
        match = re.search(version_regex, content)
        if match:
            return match.group(1)
        else:
            raise Exception("Version not found in pubspec.yaml")


def get_available_next_versions(directory_path: str) -> list[str]:
    current_version = get_version(directory_path)
    current_version = current_version.replace("+", ".")
    major, minor, patch, build = current_version.split(".")
    return [
        f"{major}.{minor}.{int(patch) + 1}+{build}",
        f"{major}.{int(minor) + 1}.0+{build}",
        f"{int(major) + 1}.0.0+{build}",
    ]


def update_version(new_version: str, directory_path: str) -> None:
    with open(f"{directory_path}/{version_file}", "r") as file:
        content = file.read()
        new_content = re.sub(version_regex, f"version: {new_version}", content)
    with open(version_file, "w") as file:
        file.write(new_content)


def tag_release(new_version: str, directory_path: str) -> None:
    # Commit the changes
    os.system(f"git -C {directory_path} add {version_file}")
    os.system(
        f"git -C {directory_path} commit -am 'Bump version to {new_version}'")

    print(f"Tagged release {new_version}")

    os.system(f"git -C {directory_path} push")


def is_dir_git_repo(directory_path: str) -> bool:
    return os.path.isdir(directory_path + "/.git")


def is_dir_flutter_project(directory_path: str) -> bool:
    return os.path.isfile(directory_path + "/pubspec.yaml")


def main(directory_path: str) -> None:
    if not is_dir_flutter_project(directory_path):
        raise Exception("This is not a Flutter project")

    print("Current version:", get_version(directory_path))
    available_versions = get_available_next_versions(directory_path)
    print("Available next versions:")
    for index, version in enumerate(available_versions):
        print(f"{index + 1}. {version}")

    new_version_number = input("Choose a new version: ")
    new_version = available_versions[int(new_version_number) - 1]
    print(f"Updating to {new_version}...")

    update_version(new_version, directory_path)

    new_git_version: str = f"v{new_version}"
    if is_dir_git_repo(directory_path):
        tag_release(new_git_version, directory_path)


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--path", help="Path to the directory containing the pubspec.yaml file", type=str, default=".", required=False)

    args = parser.parse_args()

    main(args.path)
