# Copyright (c) 2019, Chris Allison
#
#     This file is part of tvhg.
#
#     tvhg is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvhg is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvhg.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from setuptools import find_packages
from tvhg import verstr as v

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tvheadend-gui',
    version=v,
    author="Chris Allison",
    author_email="chris.charles.allison+tvhg@gmail.com",
    url="https://github.com/ccdale/tvhg",
    description="tvheadend gui application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['docs', 'test*']),
    install_requires=[
        'requests',
        ],
    python_requires='>=3',
    # entry_points={
    #     'console_scripts': [
    #         'cca=cca.cca:cca',
    #     ]
    # },
    classifiers=(
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ),
)
