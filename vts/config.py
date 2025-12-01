"""
Loads the configuration file from the XDG config directory into a
dict. For instance, $HOME/vts/config.toml
"""

from typing import Optional

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

def load_postgres_config() -> Optional[dict]:
    "Loads the PostgreSQL part of the config if it exists."
    # No config file means no PostgreSQL
    try:
        cfg = load_config()
    except OSError:
        return None
    # No database entry also means no PostgreSQL
    if "database" in cfg:
        db_cfg = cfg["database"]
        # The database entry needs two required fields
        if "username" in db_cfg and "password" in db_cfg:
            return db_cfg
    return None
