# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Omniverse microservices framework config."""

import argparse
import importlib
import json
import logging
import os
import tempfile
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import List, Optional

from asgi_correlation_id.context import correlation_id
from dynaconf import Dynaconf, Validator
from tabulate import tabulate

DEFAULT_CONFIG_PACKAGE_PATH = "config/application.toml"
SYSTEM_TMP_DIR_PATH = Path(tempfile.gettempdir())


def parse_config_argument(package_name):
    """Parse config argument from the command line."""

    parser = argparse.ArgumentParser(description=package_name)
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=None,
        required=False,
        help=f'Path to the configuration file for {package_name}.'
    )
    args, _ = parser.parse_known_args()
    # only care to get config arg.
    return args.config


def setting(*vargs, **vkwargs):
    """Dynamically build DynaConf.Validators capturing data into docstring."""

    def decorator(func):
        func.__doc__ = func.__doc__ or ""
        func.__settings__ = getattr(func, "__settings__", {})
        setting_name = vargs[0]
        if "." in setting_name:
            table_name = setting_name.split(".")[0]
        else:
            table_name = "Package Level"
        example_setting_name = setting_name
        setting_name = f"`{setting_name}`"
        setting_package = "settings_package_name"
        setting_description = vkwargs.get("description", "desc")
        cast = vkwargs.get("cast", str)
        if isinstance(cast, list):
            setting_type = f"[{cast[0].__name__}]"
        else:
            setting_type = cast.__name__
        setting_default = str(vkwargs.get("default", ""))

        if table_name in func.__settings__ and isinstance(func.__settings__[table_name], list):
            func.__settings__[table_name].append([setting_name, setting_type, setting_default, setting_description])
        else:
            func.__settings__[table_name] = [[setting_name, setting_type, setting_default, setting_description]]
        table_start_div = '<div markdown="1" class="explicit-col-width">'
        table_end_div = '</div>'
        # generate a table for each namespaced setting
        tables = []
        for k, v in func.__settings__.items():
            # customize header
            headers = [f"{k.capitalize()} Settings", "Type", "Default", "Description"]

            # make sure that Package Level is always first in the list of tables output
            if "Package Level" in k:
                tables.insert(0, tabulate(v, headers, tablefmt="pipe"))
            else:
                tables.append(tabulate(v, headers, tablefmt="pipe"))

        tables_str = ""
        for table in tables:
            tables_str += f"\n{table_start_div}\n{table}\n{table_end_div}"

        new_doc = f"""
Available Settings for {setting_package}

!!! tip "Usage"

    Please keep in mind that each setting listed should be prefixed by `{setting_package}`.

Example:

    {setting_package}.{example_setting_name}={setting_default}

        {tables_str}

        """
        func.__doc__ = new_doc

        @wraps(func)
        def wrapper(*args, **kwargs):
            validator = Validator(*vargs, **vkwargs)

            if args:
                validators = [validator] + [a for a in args]
            else:
                validators = [validator]
            return func(*validators)

        return wrapper

    return decorator


class Config:
    """
    Loads application config settings from TOML files.

    Optionally loads config from environment variable "NV__SVC__GLOBAL__CONFIG_FILEPATH"

    Args:
        package_name (str): The name of the package.
        config_filepaths (Optional[List[str]]): List of paths to config files. Defaults to None.
        validators (Optional[List[Validator]]): List of validators for configuration settings. Defaults to None.
            Validators are useful for specifying required settings for the application.
        default_config_package_path (str): The default package path for configuration files,
            relative to the package "package_name" root. Defaults to "config/application.toml".
        raise_on_package_not_found_error (bool): raise exception is the package can not be found.
        prepend_package_name (bool): Prepends the package name to the validator settings.
        auto_configure_logging (bool): Configures logging for the application.
        logging_config (Config): The logging config.

    Raises:
        ModuleNotFoundError: If the specified package "package_name" module cannot be imported.

    Attributes:
        settings (Dynaconf): An instance of Dynaconf to manage configuration settings.
            Individual settings can be accessed via this object. e.g "self.settings.foo", or nested "self.settings.foo.bar.baz"

    """

    _DEFAULT_APP_NAMESPACE = "nv.svc"
    _validators = []

    def __init__(
        self,
        package_name: str,
        config_filepaths: Optional[List[str]] = None,
        validators: Optional[List[Validator]] = None,
        default_config_package_path: str = DEFAULT_CONFIG_PACKAGE_PATH,
        raise_on_package_not_found_error: bool = True,
        prepend_package_name: bool = True,
        auto_configure_logging: bool = False,
        logging_config=None,
    ):
        """Initialize Config with package name, config file paths, validators, and default package path."""
        if not config_filepaths:
            config_filepaths = []
        self._validators = validators or self._validators
        self.package_name = package_name
        if prepend_package_name:
            for validator in self._validators:
                validator.names = (f"{self.package_name}.{validator.names[0]}",)
        self.package_version = None
        package_module = None
        try:
            package_module = importlib.import_module(self.package_name)
        except ModuleNotFoundError:
            if raise_on_package_not_found_error:
                raise

        try:
            distribution = importlib.metadata.distribution(self.package_name)
            self.package_version = distribution.version
        except importlib.metadata.PackageNotFoundError:
            if raise_on_package_not_found_error:
                raise

        if package_module is not None:
            default_config_location = Path(package_module.__file__).resolve().parent / default_config_package_path
            if default_config_location.exists():
                # ensure default config is loaded first.
                config_filepaths = [str(default_config_location)] + config_filepaths

        _nested_separator = "__"
        _backaward_compat_pkg_config_fp = os.environ.get(f"{self.package_name.upper()}.CONFIG_FILEPATH")
        envvar_config_filepath = os.environ.get(f"{self.package_name.upper().replace('.', _nested_separator)}{_nested_separator}CONFIG_FILEPATH")
        if not envvar_config_filepath:
            # fallback to old version using `.`
            envvar_config_filepath = _backaward_compat_pkg_config_fp
        if envvar_config_filepath is not None and Path(envvar_config_filepath).exists():
            config_filepaths.append(envvar_config_filepath)

        _backaward_compat_global_config_fp = os.environ.get("NV.SVC.GLOBAL.CONFIG_FILEPATH")
        global_config_filepath = os.environ.get(f"NV{_nested_separator}SVC{_nested_separator}GLOBAL{_nested_separator}CONFIG_FILEPATH")
        if not global_config_filepath:
            # fallback to old version using `.`
            global_config_filepath = _backaward_compat_global_config_fp
        if global_config_filepath is not None and Path(global_config_filepath).exists():
            config_filepaths.append(global_config_filepath)

        # inspect CLI -c/--config and take precedence over all config files
        cliarg_config_filepath = parse_config_argument(package_name)
        if cliarg_config_filepath is not None and Path(cliarg_config_filepath).exists():
            config_filepaths.append(cliarg_config_filepath)

        # most commonly used in unit tests, provide backawards compatability temporarily
        for envvar in ("NV.SVC.SERVER.HTTP.HTTP.ENABLED", f"{self.package_name.upper()}.PREFIX_URL"):
            if envvar in os.environ:
                os.environ[envvar.replace(".", _nested_separator)] = os.environ[envvar]

        self.settings = Dynaconf(
            settings_files=config_filepaths,
            core_loaders=["TOML", "YAML"],
            load_dotenv=False,
            environments=True,
            envvar_prefix=False,
            nested_separator=_nested_separator,
            dotted_lookup=True,
            default_env="settings",
            env="settings",
            merge_enabled=True,
            apply_default_on_none=True,
            validators=self._validators,
        )
        self.logging_config = logging_config

        if auto_configure_logging:
            self.configure_logging()

        cp_str = ", ".join([str(c) for c in config_filepaths])
        logging.debug(f"package: '{self.package_name}' loaded '{len(config_filepaths)}' config filepaths to merge: '{cp_str}'")

    def configure_logging(self, logger: logging.Logger = None):
        """Configure logging for the application.

        Utilizes settings from `nv.svc.core.logging` for the logging level.

        Args:
            logger (Optional(logging.Logger)): A preconfigured logger, or name to use when getting the logger to configure.
                NOTE: will overwrite any preconfigured handlers and formatters.
                DEFAULT: the root logger
        """
        if self.logging_config is None:
            from ..config import ServicesCoreLoggingConfig
            self.logging_config = ServicesCoreLoggingConfig()

        log_level = self.logging_config.logging.log_level
        _configure_logging(logger=logger, log_level=log_level)

    def __getattr__(self, name):
        """
        Customize attribute retrieval for Config settings.

        First looks at the internal Settings object using the package name then fallsback to instance attributes.

        Args:
            name (str): The name of the setting under the package_name or instance attribute.

        Returns:
            The value of the attribute if found.

        Raises:
            AttributeError: If the attribute is not found in both the usual way and
                in the settings object.

        """
        try:
            return getattr(self.settings, f"{self.package_name}.{name}")
        except AttributeError:
            return super().__getattribute__(name)

    def get_settings_dict(self) -> dict:
        """Retrieve the loaded settings as a dictionary.

        Returns:
            dict: The loaded settings as a dictionary.

        """
        return self.settings.to_dict()


class _JsonFormatter(logging.Formatter):
    """JSON formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        # Include extra fields (anything passed via `extra=`)
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__:
                log[key] = value

        return json.dumps(log)


class _CorrelationIDFilter(logging.Filter):
    def filter(self, record):
        cid = correlation_id.get()
        if cid is not None:
            record.__dict__["correlation_id"] = cid

        return True


def _configure_logging(logger: logging.Logger = None, log_level: str = "INFO"):
    """Configure the logger with the given level and add a JSON handler with a correlation ID filter.

    Args:
        logger (logging.Logger): The logger to setup.
        log_level (str): The logging level.
    """
    if logger is None:
        logger = logging.getLogger()

    logger.propagate = False
    logger.setLevel(log_level)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.addFilter(_CorrelationIDFilter())
