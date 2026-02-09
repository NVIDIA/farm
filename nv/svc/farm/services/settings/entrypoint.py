# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Farm Settings Service Entrypoint."""

import logging

from nv.svc.core.main import ServicesCore
from nv.svc.server.http import HTTPServer
from nv.svc.farm.utils import configure_default_config_filepath


def configure_settings_service(core: ServicesCore = None) -> ServicesCore:
    """Configure settings service with service core."""

    configure_default_config_filepath()

    from nv.svc.farm.services.settings.config import FarmSettingsConfig
    from nv.svc.farm.services.settings.facility import ServiceSettingsFacility
    from nv.svc.farm.services.settings.stores import DynaConfSettingsStore
    from nv.svc.farm.services.settings.api import router

    config = FarmSettingsConfig()

    logging.info("Configuring Settings service.")

    # required because of clash between "settings" and the first key after the package name
    settings = config.settings.nv.svc.farm.settings

    if not core:
        core = ServicesCore(
            title=f"{config.package_name}-settings",
            description="Farm Settings Service.",
            version=config.package_version,
        )
    settings_facilities = ServiceSettingsFacility(settings_store=DynaConfSettingsStore(settings=config))
    core.register_facility("settings", settings_facilities)
    core.register_router(router, prefix=settings.url_prefix, tags=["settings"])


def main():
    """Configure and run the application with an HTTP server if enabled."""
    configure_settings_service()

    server = HTTPServer()
    server.on_startup()


if __name__ == "__main__":
    main()
