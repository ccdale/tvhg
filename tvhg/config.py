#
# Copyright (c) 2018, Christopher Allison
#
#     This file is part of tvh.
#
#     tvh is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvh is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvh.  If not, see <http://www.gnu.org/licenses/>.
"""
config module for tvh application
"""
import sys
import yaml
from pathlib import Path
from tvheadend.errors import errorExit


def writeConfig(config):
    try:
        yamlfn = "tvh.yaml"
        home = Path.home()
        configfn = home.joinpath(".config", yamlfn)
        with open(str(configfn), "w") as cfn:
            yaml.dump(config, cfn, default_flow_style=False)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e, 1)


def readConfig():
    config = {}
    try:
        yamlfn = "tvh.yaml"
        home = Path.home()
        configfn = home.joinpath(".config", yamlfn)
        with open(str(configfn), "r") as cfn:
            config = yaml.safe_load(cfn)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e, 1)
    finally:
        return config
