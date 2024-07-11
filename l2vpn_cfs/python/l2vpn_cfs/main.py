# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import requests

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        headers = {"Authorization":"Token e657404c0e1f57481ad0a06c293e8fe794e720ac", "Accept": "application/json", "Content-Type": "application/json"}
        body = {}

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        for endpoint in service.endpoint:

            # Get an Outer VLAN from Netbox. The VLAN group for outer VLAN's is #2.
            api_url="https://10.101.180.45/api/ipam/vlan-groups/2/available-vlans/"
            ovlan_name = "L2VPN-Outer-VLAN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            body = {"name": ovlan_name}
            try:
                response=requests.post(api_url, headers=headers, json=body, verify=False)
                self.log.info('Netbox response, Outer VLAN reservation: ', response.json())
                ovlan_id = response.json()["vid"]
                self.log.info('VLAN from Netbox: ', ovlan_id)
            except:
                if endpoint.ovlan:
                    ovlan_id = endpoint.ovlan
                else:
                    ovlan_id = 254
                self.log.info('Connection to Netbox failed. Statically allocated Outer VLAN: ', ovlan_id)
            vars.add('ovlan', ovlan_id)

            # Get an Inner VLAN from Netbox. The VLAN group for inner VLAN's is #3.
            api_url="https://10.101.180.45/api/ipam/vlan-groups/3/available-vlans/"
            ivlan_name = "L2VPN-Inner-VLAN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            body = {"name": ivlan_name}
            try:
                response=requests.post(api_url, headers=headers, json=body, verify=False)
                self.log.info('Netbox response, Inner VLAN reservation: ', response.json())
                ivlan_id = response.json()["vid"]
                self.log.info('VLAN from Netbox: ', ivlan_id)
            except:
                if endpoint.ivlan:
                    ivlan_id = endpoint.ivlan
                else:
                    ivlan_id = 253
                self.log.info('Connection to Netbox failed. Statically allocated Inner VLAN: ', ivlan_id)
            vars.add('ivlan', ivlan_id)

            # PE part
            name = "L2VPN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Name for PE instance: ', name)
            vars.add('pe_device', endpoint.pe_device)
            vars.add('bridge_group_name', str(endpoint.id))
            # PE to Switch interface configuration:
            vars.add('pe_interface_name', endpoint.pe_interface.interface_name)
            vars.add('pe_interface_number', endpoint.pe_interface.interface_number)
            pe_interface_description = "L2VPN interface to " + str(endpoint.sw_device) + ", interface " + str(endpoint.sw_pe_interface.interface_name) + str(endpoint.sw_pe_interface.interface_number)
            vars.add('pe_interface_description', pe_interface_description)
            self.log.info('pe_interface_description: ', pe_interface_description)
            template.apply('l2vpn_pe-template', vars)

            # Switch part
            name = "L2VPN-"+str(endpoint.sw_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Name for Switch instance: ', name)
            vars.add('sw_device', endpoint.sw_device)
            vars.add('vlan_name', str(endpoint.id))
            # Switch to PE interface configuration:
            vars.add('sw_pe_interface_name', endpoint.sw_pe_interface.interface_name)
            vars.add('sw_pe_interface_number', endpoint.sw_pe_interface.interface_number)
            sw_pe_interface_description = "L2VPN interface to " + str(endpoint.pe_device) + ", interface " + str(endpoint.pe_interface.interface_name) + str(endpoint.pe_interface.interface_number)
            vars.add('sw_pe_interface_description', sw_pe_interface_description)
            self.log.info('sw_pe_interface_description: ', sw_pe_interface_description)
            # Switch to CPE interface configuration:
            vars.add('sw_cpe_interface_name', endpoint.sw_cpe_interface.interface_name)
            vars.add('sw_cpe_interface_number', endpoint.sw_cpe_interface.interface_number)
            sw_cpe_interface_description = "L2VPN interface to " + str(endpoint.cpe_device) + ", interface " + str(endpoint.cpe_interface.interface_name) + str(endpoint.cpe_interface.interface_number)
            vars.add('sw_cpe_interface_description', sw_cpe_interface_description)
            self.log.info('sw_cpe_interface_description: ', sw_cpe_interface_description)
            template.apply('l2vpn_sw-template', vars)

            # CPE part
            name = "L2VPN-"+str(endpoint.cpe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Name for CPE instance: ', name)
            vars.add('cpe_device', endpoint.cpe_device)
            vars.add('vlan_name', str(endpoint.id))
            # CPE to Switch interface configuration:
            vars.add('cpe_interface_name', endpoint.cpe_interface.interface_name)
            vars.add('cpe_interface_number', endpoint.cpe_interface.interface_number)
            cpe_interface_description = "L2VPN interface to " + str(endpoint.sw_device) + ", interface " + str(endpoint.sw_cpe_interface.interface_name) + str(endpoint.sw_cpe_interface.interface_number)
            vars.add('cpe_interface_description', cpe_interface_description)
            self.log.info('cpe_interface_description: ', cpe_interface_description)
            template.apply('l2vpn_cpe-template', vars)


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l2vpn_cfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
