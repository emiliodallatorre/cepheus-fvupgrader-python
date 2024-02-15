#!/usr/bin/env python3

import os
import re

version_regex: str = r"version: (\d+\.\d+\.\d+\+\d+)"
version_file: str = "pubspec.yaml"


def get_version() -> str:
    with open(version_file, "r") as file:
        content = file.read()
        match = re.search(version_regex, content)
        if match:
            return match.group(1)
        else:
            raise Exception("Version not found in pubspec.yaml")


def get_available_next_versions() -> list[str]:
    current_version = get_version()
    current_version = current_version.replace("+", ".")
    major, minor, patch, build = current_version.split(".")
    return [
        f"{major}.{minor}.{int(patch) + 1}+{build}",
        f"{major}.{int(minor) + 1}.0+{build}",
        f"{int(major) + 1}.0.0+{build}",
    ]


def update_version(new_version: str) -> None:
    with open(version_file, "r") as file:
        content = file.read()
        new_content = re.sub(version_regex, f"version: {new_version}", content)
    with open(version_file, "w") as file:
        file.write(new_content)


def tag_release(new_version: str) -> None:
    os.system(
        f"git tag -a {new_version} -m 'Avanzato il numero di versione ({new_version}).'")
    os.system(f"git push origin {new_version}")

    print(f"Tagged release {new_version}")

    os.system("git push origin main")


def is_current_dir_git_repo() -> bool:
    return os.path.isdir(".git")


def main() -> None:
    print("Current version:", get_version())
    available_versions = get_available_next_versions()
    print("Available next versions:")
    for index, version in enumerate(available_versions):
        print(f"{index + 1}. {version}")

    new_version_number = input("Choose a new version: ")
    new_version = available_versions[int(new_version_number) - 1]
    print(f"Updating to {new_version}...")

    update_version(new_version)
    if is_current_dir_git_repo():
        tag_release(new_version)


if __name__ == "__main__":
    main()
