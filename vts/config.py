"""
Loads the configuration file from the XDG config directory into a
dict. For instance, $HOME/vts/config.toml
"""

import os
import tomllib

from xdg_base_dirs import xdg_config_home

def load_config() -> dict:
    "Loads the config.toml file from the vts directory."
    cfg_dir = os.path.join(xdg_config_home(), "vts/")
    cfg_path = os.path.join(cfg_dir, "config.toml")

    with open(cfg_path, "rb") as file:
        cfg = tomllib.load(file)

    return cfg
