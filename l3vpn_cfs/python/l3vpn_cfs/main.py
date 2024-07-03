# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)
        for endpoint in service.endpoint:
            # PE part
            name = "L3VPN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            vars.add('pe_device', endpoint.pe_device)
            # vars.add('as_number', endpoint.as_number)
            # vars.add('remote_as_number', endpoint.customer_as_number)
            vars.add('cpe_interface_address', endpoint.cpe_interface.ipv4_address)
            vars.add('pe_interface_name', endpoint.pe_interface.interface_name)
            vars.add('pe_interface_number', endpoint.pe_interface.interface_number)
            pe_interface_description = "L3VPN interface to " + str(endpoint.cpe_device) + ", interface " + str(endpoint.cpe_interface.interface_name) + str(endpoint.cpe_interface.interface_number)
            vars.add('pe_interface_description', pe_interface_description)
            # vars.add('pe_interface_description', endpoint.pe_interface.interface_description)
            vars.add('pe_ipv4_address', endpoint.pe_interface.ipv4_address)
            vars.add('pe_ipv4_mask', endpoint.pe_interface.ipv4_mask)
            template.apply('l3vpn_pe-template', vars)

            # CPE part
            name = "L3VPN-"+str(endpoint.cpe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            vars.add('cpe_device', endpoint.cpe_device)
            # vars.add('remote_as_number', endpoint.as_number)
            # vars.add('as_number', endpoint.customer_as_number)
            vars.add('pe_interface_address', endpoint.pe_interface.ipv4_address)
            vars.add('cpe_loopback0_address', endpoint.cpe_loopback0_address)
            vars.add('cpe_loopback0_mask', '255.255.255.255')
            vars.add('cpe_interface_name', endpoint.cpe_interface.interface_name)
            vars.add('cpe_interface_number', endpoint.cpe_interface.interface_number)
            cpe_interface_description = "L3VPN interface to " + str(endpoint.pe_device) + ", interface " + str(endpoint.pe_interface.interface_name) + str(endpoint.pe_interface.interface_number)
            vars.add('cpe_interface_description', cpe_interface_description)
            # vars.add('cpe_interface_description', endpoint.cpe_interface.interface_description)
            vars.add('cpe_ipv4_address', endpoint.cpe_interface.ipv4_address)
            vars.add('cpe_ipv4_mask', endpoint.cpe_interface.ipv4_mask)
            template.apply('l3vpn_cpe-template', vars)

            if endpoint.qos.enable_qos_policy:
                pe_bit_rate = endpoint.qos.bit_rate
                cpe_bit_rate = 1000 * endpoint.qos.bit_rate
                vars.add('pe_bit_rate', pe_bit_rate)
                vars.add('cpe_bit_rate', cpe_bit_rate)
                name = "L3VPN-QoS-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
                template.apply('l3vpn_pe_qos-template', vars)
                name = "L3VPN-QoS-"+str(endpoint.cpe_device)+"-"+str(endpoint.id)
                template.apply('l3vpn_cpe_qos-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_cfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
