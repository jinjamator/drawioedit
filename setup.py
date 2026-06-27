import setuptools
import os
import re
from subprocess import check_output

command = "git describe --tags --dirty"


def format_version(describe):
    """Turn ``git describe --tags --dirty`` output into a PEP 440 version.

    Handles the four forms it can emit::

        <tag>
        <tag>-dirty
        <tag>-<count>-g<sha>
        <tag>-<count>-g<sha>-dirty

    Commits ahead of the tag become a ``.devN`` release; the short sha and a
    dirty working tree are encoded as PEP 440 local version labels (after ``+``)
    so e.g. ``0.4.2-dirty`` -> ``0.4.2+dirty`` instead of an invalid version.
    """
    match = re.match(
        r"^(?P<tag>.+?)"
        r"(?:-(?P<count>\d+)-g(?P<sha>[0-9a-f]+))?"
        r"(?:-(?P<dirty>dirty))?$",
        describe,
    )
    tag, count, sha, dirty = match.group("tag", "count", "sha", "dirty")
    version = f"{tag}.dev{count}" if count and count != "0" else tag
    local = [part for part in (f"g{sha}" if sha else None, dirty) if part]
    if local:
        version += "+" + ".".join(local)
    return version


version = format_version(check_output(command.split()).decode("utf-8").strip())


with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split("\n")

setuptools.setup(
    name="drawioedit",
    version=version,
    author="Wilhelm Putz",
    author_email="wp@aci.guru",
    description="Simple interface to edit drawio files",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jinjamator/drawioedit",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*"]},
    install_requires=install_requires,
    license="ASL V2",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)
