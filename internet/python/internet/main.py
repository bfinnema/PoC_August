# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vlan_octet = service.vlan_id % 256
        vars.add('vlan_octet', vlan_octet)
        self.log.info('VLAN Octet: ', vlan_octet)
        sw_loopback_if_octet = (service.vlan_id + 100) % 256
        sw_loopback_if_ipv4addr = str(sw_loopback_if_octet) + "." + str(sw_loopback_if_octet) + "." + str(sw_loopback_if_octet) + ".1"
        vars.add('sw_loopback_if_ipv4addr', sw_loopback_if_ipv4addr)
        sw_loopback_if_ipv4net = str(sw_loopback_if_octet) + "." + str(sw_loopback_if_octet) + "." + str(sw_loopback_if_octet) + ".0"
        vars.add('sw_loopback_if_ipv4net', sw_loopback_if_ipv4net)
        vars.add('sw_loopback_if_ipv4mask', "255.255.255.0")
        pe_interface_description = "Interface for Internet service to " + str(service.sw_device) + ", interface " + str(service.sw_interface.interface_name) + str(service.sw_interface.interface_number)
        vars.add('pe_interface_description', pe_interface_description)
        sw_interface_description = "Interface for Internet service to " + str(service.pe_device) + ", interface " + str(service.pe_interface.interface_name) + str(service.pe_interface.interface_number)
        vars.add('sw_interface_description', sw_interface_description)
        bgp_neighbor_description = "BGP neighbor for internet service to " + str(service.pe_device)
        vars.add('bgp_neighbor_description', bgp_neighbor_description)

        template = ncs.template.Template(service)
        template.apply('internet_pe-template', vars)
        template.apply('internet_sw-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('internet-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
