"""
Loads the configuration file from the XDG config directory into a
dict. For instance, $HOME/vts/config.toml
"""

from typing import Optional

import os
import tomllib

from xdg_base_dirs import xdg_config_home

class ConfigPathError(Exception):
    "Error if the config file or directory is not found."

def get_config_path():
    "Retrieve the configuration path."
    cfg_dir = os.path.join(xdg_config_home(), "vts/")
    return os.path.join(cfg_dir, "config.toml")

def load_config() -> dict:
    "Loads the config.toml file from the vts directory."
    cfg_path = get_config_path()

    try:
        with open(cfg_path, "rb") as file:
            cfg = tomllib.load(file)
    # Ignore Pylint's suggestion, we only need the path here.
    #
    # pylint:disable=raise-missing-from
    except FileNotFoundError:
        raise ConfigPathError(get_config_path())

    return cfg

def load_postgres_config() -> Optional[dict]:
    "Loads the PostgreSQL part of the config if it exists."
    # No config file means no PostgreSQL
    try:
        cfg = load_config()
    except ConfigPathError:
        return None
    # No database entry also means no PostgreSQL
    if "database" in cfg:
        db_cfg = cfg["database"]
        # The database entry needs two required fields
        if "username" in db_cfg and "password" in db_cfg:
            return db_cfg
    return None
