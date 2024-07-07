# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import requests

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        api_url="http://10.101.180.45/api/ipam/prefixes/1/available-ips/"
        headers = {"Authorization":"Token e657404c0e1f57481ad0a06c293e8fe794e720ac"}

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)
        for endpoint in service.endpoint:
            # PE part
            response=requests.get(api_url, headers=headers, verify=False)
            self.log.info('Netbox response: ', response.json)
            ipv4_address = response.json["address"]
            self.log.info('Address: ', ipv4_address)

            name = "L3VPN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            vars.add('pe_device', endpoint.pe_device)
            vars.add('cpe_interface_address', endpoint.cpe_interface.ipv4_address)
            vars.add('pe_interface_name', endpoint.pe_interface.interface_name)
            vars.add('pe_interface_number', endpoint.pe_interface.interface_number)
            pe_interface_description = "L3VPN interface to " + str(endpoint.cpe_device) + ", interface " + str(endpoint.cpe_interface.interface_name) + str(endpoint.cpe_interface.interface_number)
            vars.add('pe_interface_description', pe_interface_description)
            vars.add('pe_ipv4_address', endpoint.pe_interface.ipv4_address)
            vars.add('pe_ipv4_mask', endpoint.pe_interface.ipv4_mask)
            self.log.info('ipv4_mask: ', endpoint.pe_interface.ipv4_mask)
            template.apply('l3vpn_qinq_pe-template', vars)


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_qinq_cfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
