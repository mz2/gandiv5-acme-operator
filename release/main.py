#!/usr/bin/env python3

import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
parser.add_argument("--charm", required=True)
parser.add_argument("--resource-name", required=True)
parser.add_argument("--charm-path", required=True)

args = parser.parse_args()

image_name, tag = args.image.rsplit(":", 1)

pull_command = subprocess.run(["docker", "pull", args.image], check=True)
if pull_command.returncode != 0:
    exit(pull_command.returncode)

digest_command = subprocess.run(
    [
        "docker",
        "images",
        "--digests",
        "--no-trunc",
        "--format",
        "{{.Digest}}",
        image_name,
    ],
    check=True,
    capture_output=True,
    text=True,
)
if digest_command.returncode != 0:
    exit(digest_command.returncode)
digest = digest_command.stdout.strip()
print(f"Digest of image: {digest}")

upload_resource_command = subprocess.run(
    [
        "charmcraft",
        "upload-resource",
        "--image",
        digest,
        args.charm,
        args.resource_name,
    ],
    check=True,
    capture_output=True,
    text=True,
)
if upload_resource_command.returncode != 0:
    exit(upload_resource_command.returncode)

output_lines = upload_resource_command.stdout.splitlines()
for line in output_lines:
    if line.startswith("Revision"):
        resource_revision = line.split()[1]
        print(f"Revision of resource: {resource_revision}")

upload_charm_command = subprocess.run(
    ["charmcraft", "upload", args.charm_path], check=True
)
if upload_charm_command.returncode != 0:
    exit(upload_charm_command.returncode)

revisions_command = subprocess.run(
    ["charmcraft", "revisions", args.charm], check=True, capture_output=True, text=True
)
if revisions_command.returncode != 0:
    exit(revisions_command.returncode)

output_lines = revisions_command.stdout.splitlines()
for line in output_lines:
    if line.startswith("1"):
        charm_revision = line.split()[0]
        print(f"Revision of charm: {charm_revision}")

release_command = subprocess.run(
    [
        "charmcraft",
        "release",
        args.charm,
        "--revision",
        charm_revision,
        "--channel=beta",
        f"--resource={args.resource_name}:{resource_revision}",
    ],
    check=True,
)
if release_command.returncode != 0:
    exit(release_command.returncode)
