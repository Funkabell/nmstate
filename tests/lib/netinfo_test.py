#
# Copyright (c) 2018-2019 Red Hat, Inc.
#
# This file is part of nmstate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
import pytest

from unittest import mock

from libnmstate import netinfo
from libnmstate.schema import Constants
from libnmstate.schema import DNS
from libnmstate.schema import RouteRule
from libnmstate.schema import InterfaceIPv4
from libnmstate.schema import InterfaceIPv6


INTERFACES = Constants.INTERFACES
ROUTES = Constants.ROUTES


@pytest.fixture
def nm_mock():
    with mock.patch.object(netinfo, "nm") as m:
        m.ipv4.get_routing_rule_config.return_value = []
        m.ipv6.get_routing_rule_config.return_value = []
        yield m


@pytest.fixture
def nm_dns_mock():
    with mock.patch.object(netinfo, "nm_dns") as m:
        yield m


def test_netinfo_show_generic_iface(nm_mock, nm_dns_mock):
    current_config = {
        DNS.KEY: {DNS.RUNNING: {}, DNS.CONFIG: {}},
        ROUTES: {"config": [], "running": []},
        RouteRule.KEY: {RouteRule.CONFIG: []},
        INTERFACES: [
            {
                "name": "foo",
                "type": "unknown",
                "state": "up",
                "ipv4": {InterfaceIPv4.ENABLED: False},
                "ipv6": {InterfaceIPv6.ENABLED: False},
            }
        ],
    }

    current_iface0 = current_config[INTERFACES][0]
    nm_mock.device.list_devices.return_value = ["one-item"]
    nm_mock.translator.Nm2Api.get_common_device_info.return_value = (
        current_iface0
    )
    nm_mock.bond.is_bond_type_id.return_value = False
    nm_mock.ipv4.get_info.return_value = current_iface0["ipv4"]
    nm_mock.ipv6.get_info.return_value = current_iface0["ipv6"]
    nm_mock.ipv4.get_route_running.return_value = []
    nm_mock.ipv4.get_route_config.return_value = []
    nm_mock.ipv6.get_route_running.return_value = []
    nm_mock.ipv6.get_route_config.return_value = []
    nm_dns_mock.get_running.return_value = current_config[DNS.KEY][DNS.RUNNING]
    nm_dns_mock.get_config.return_value = current_config[DNS.KEY][DNS.CONFIG]

    report = netinfo.show()

    assert current_config == report


def test_netinfo_show_bond_iface(nm_mock, nm_dns_mock):
    current_config = {
        DNS.KEY: {DNS.RUNNING: {}, DNS.CONFIG: {}},
        ROUTES: {"config": [], "running": []},
        RouteRule.KEY: {RouteRule.CONFIG: []},
        INTERFACES: [
            {
                "name": "bond99",
                "type": "bond",
                "state": "up",
                "link-aggregation": {
                    "mode": "balance-rr",
                    "slaves": [],
                    "options": {"miimon": "100"},
                },
                "ipv4": {InterfaceIPv4.ENABLED: False},
                "ipv6": {InterfaceIPv6.ENABLED: False},
            }
        ],
    }

    nm_mock.device.list_devices.return_value = ["one-item"]
    nm_mock.translator.Nm2Api.get_common_device_info.return_value = {
        "name": current_config[INTERFACES][0]["name"],
        "type": current_config[INTERFACES][0]["type"],
        "state": current_config[INTERFACES][0]["state"],
    }
    nm_mock.bond.is_bond_type_id.return_value = True
    nm_mock.translator.Nm2Api.get_bond_info.return_value = {
        "link-aggregation": current_config[INTERFACES][0]["link-aggregation"]
    }
    nm_mock.ipv4.get_info.return_value = current_config[INTERFACES][0]["ipv4"]
    nm_mock.ipv6.get_info.return_value = current_config[INTERFACES][0]["ipv6"]
    nm_mock.ipv4.get_route_running.return_value = []
    nm_mock.ipv4.get_route_config.return_value = []
    nm_mock.ipv6.get_route_running.return_value = []
    nm_mock.ipv6.get_route_config.return_value = []
    nm_dns_mock.get_running.return_value = current_config[DNS.KEY][DNS.RUNNING]
    nm_dns_mock.get_config.return_value = current_config[DNS.KEY][DNS.CONFIG]

    report = netinfo.show()

    assert current_config == report
