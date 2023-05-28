#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

import logging
from typing import Dict

import ops
from charms.acme_client_operator.v0.acme_client import AcmeClient
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class GandiLiveDNSVersion5AcmeOperatorCharm(AcmeClient):
    """Charm the service."""

    REQUIRED_CONFIG = ["GANDIV5_API_KEY"]

    def __init__(self, *args):
        """Use the acme_client library to manage events."""
        super().__init__(*args, plugin="gandiv5")
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    @property
    def _gandi_api_key(self) -> str:
        return self.model.config.get("gandi_api_key")

    @property
    def _gandi_http_timeout(self) -> str | None:
        return self.model.config.get("gandi_http_timeout")

    @property
    def _gandi_polling_interval(self) -> str | None:
        return self.model.config.get("gandi_polling_interval")

    @property
    def _gandi_propagation_timeout(self) -> str | None:
        return self.model.config.get("gandi_propagation_timeout")

    @property
    def _gandi_ttl(self) -> str | None:
        return self.model.config.get("gandi_ttl")

    @property
    def _plugin_config(self) -> Dict[str, str]:
        additional_config = {
            "GANDIV5_API_KEY": self._gandi_api_key,
        }
        if self._gandi_http_timeout:
            additional_config["GANDIV5_HTTP_TIMEOUT"] = self._gandi_http_timeout
        if self._gandi_polling_interval:
            additional_config["GANDIV5_POLLING_INTERVAL"] = self._gandi_polling_interval
        if self._gandi_propagation_timeout:
            additional_config["GANDIV5_PROPAGATION_TIMEOUT"] = self._gandi_propagation_timeout
        if self._gandi_ttl:
            additional_config["GANDIV5_TTL"] = self._gandi_ttl
        return additional_config

    def _validate_gandi_livedns_config(self) -> bool:
        if missing_config := [
            option for option in self.REQUIRED_CONFIG if not self._plugin_config[option]
        ]:
            msg = f"The following config options must be set: {', '.join(missing_config)}"
            self.unit.status = BlockedStatus(msg)
            return False
        return True

    def _on_config_changed(self, _) -> None:
        if not self._validate_gandi_livedns_config():
            return
        if not self.validate_generic_acme_config():
            return
        self.unit.status = ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(GandiLiveDNSVersion5AcmeOperatorCharm)
