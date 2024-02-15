#!/usr/bin/env python3

import os.path
import re
from argparse import ArgumentParser

fvupgrader_version: str = "1.0.0"

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
    with open(f"{directory_path}/{version_file}", "w") as file:
        file.write(new_content)


def git_operations(new_version: str, directory_path: str, args) -> None:
    # Commit the changes
    if not args.no_commit:
        os.system(f"git -C {directory_path} add {version_file}")
        os.system(
            f"git -C {directory_path} commit -am 'Bump version to {new_version}'")

    # Tag the release
    if not args.no_tag:
        os.system(f"git -C {directory_path} tag {new_version}")
        print(f"Tagged release {new_version}")

    # Push the changes
    if not args.no_push:
        os.system(f"git -C {directory_path} push")


def is_dir_git_repo(directory_path: str) -> bool:
    return os.path.isdir(directory_path + "/.git")


def is_dir_flutter_project(directory_path: str) -> bool:
    return os.path.isfile(directory_path + "/pubspec.yaml")


def main(args) -> None:
    directory_path = os.path.abspath(args.path)

    if not is_dir_flutter_project(directory_path):
        raise Exception("This is not a Flutter project")

    print("Current version:", get_version(directory_path))
    available_versions = get_available_next_versions(directory_path)

    if not args.major and not args.minor and not args.patch:
        print("Available next versions:")
        for index, version in enumerate(available_versions):
            print(f"{index + 1}. {version}")

        new_version_number = input("Choose a new version: ")
        new_version = available_versions[int(new_version_number) - 1]
    else:
        if args.major:
            new_version = available_versions[2]
        elif args.minor:
            new_version = available_versions[1]
        elif args.patch:
            new_version = available_versions[0]

    print(f"Updating to {new_version}...")

    update_version(new_version, directory_path)

    new_git_version: str = f"v{new_version}"
    if is_dir_git_repo(directory_path):
        git_operations(new_git_version, directory_path, args)


def fix_args(args) -> ArgumentParser:
    if not args.no_push and args.no_commit:
        raise Exception("You cannot push without committing")
    if not args.no_tag and args.no_commit:
        raise Exception("You cannot tag without committing")

    if args.major and args.minor:
        raise Exception(
            "You cannot upgrade the major and minor versions at the same time")
    if args.major and args.patch:
        raise Exception(
            "You cannot upgrade the major and patch versions at the same time")
    if args.minor and args.patch:
        raise Exception(
            "You cannot upgrade the minor and patch versions at the same time")

    return args


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--path", help="path to the directory containing the pubspec.yaml file", type=str, default=".", required=False
    )
    parser.add_argument(
        "--no-push", help="push the changes to the git repository", action="store_true", default=False
    )
    parser.add_argument(
        "--no-commit", help="commit the changes to the git repository", action="store_true", default=False
    )
    parser.add_argument(
        "--no-tag", help="tag the release in the git repository", action="store_true", default=False
    )
    parser.add_argument(
        "--major", help="upgrade the major version", action="store_true", default=False
    )
    parser.add_argument(
        "--minor", help="upgrade the minor version", action="store_true", default=False
    )
    parser.add_argument(
        "--patch", help="upgrade the patch version", action="store_true", default=False
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s v{fvupgrader_version}"
    )

    args = parser.parse_args()
    args = fix_args(args)

    main(args)
