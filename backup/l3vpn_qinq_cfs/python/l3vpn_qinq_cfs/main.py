# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import requests
import socket
import struct

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        def cidr_to_netmask(cidr):
            network, net_bits = cidr.split('/')
            host_bits = 32 - int(net_bits)
            netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
            return network, netmask, net_bits

        headers = {"Authorization":"Token e657404c0e1f57481ad0a06c293e8fe794e720ac", "Accept": "application/json", "Content-Type": "application/json"}
        body = {}

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)
        for endpoint in service.endpoint:
            # PE part
            # Get an IP address from Netbox for the PE VPN interface
            api_url="https://10.101.180.45/api/ipam/prefixes/1/available-ips/"
            response=requests.post(api_url, headers=headers, json=body, verify=False)
            self.log.info('Netbox response, IP address reservation: ', response.json())
            ipv4_cidr = response.json()["address"]
            self.log.info('CIDR from Netbox: ', ipv4_cidr)
            ipv4_address, ipv4_mask, ipv4_cidr_mask = cidr_to_netmask(ipv4_cidr)
            self.log.info('Address: ', ipv4_address)
            self.log.info('Net Mask: ', ipv4_mask)
            self.log.info('CIDR Mask: ', ipv4_cidr_mask)
            vars.add('pe_ipv4_address', ipv4_address)
            vars.add('pe_ipv4_mask', ipv4_mask)

            # Get an Outer VLAN from Netbox. The VLAN group for outer VLAN's is #2.
            api_url="https://10.101.180.45/api/ipam/vlan-groups/2/available-vlans/"
            ovlan_name = "L3VPN-Outer-VLAN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            body = {"name": ovlan_name}
            response=requests.post(api_url, headers=headers, json=body, verify=False)
            self.log.info('Netbox response, Outer VLAN reservation: ', response.json())
            ovlan_id = response.json()["vid"]
            self.log.info('VLAN from Netbox: ', ovlan_id)
            vars.add('ovlan', ovlan_id)

            # Get an Inner VLAN from Netbox. The VLAN group for inner VLAN's is #3.
            api_url="https://10.101.180.45/api/ipam/vlan-groups/3/available-vlans/"
            ivlan_name = "L3VPN-Inner-VLAN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            body = {"name": ivlan_name}
            response=requests.post(api_url, headers=headers, json=body, verify=False)
            self.log.info('Netbox response, Inner VLAN reservation: ', response.json())
            ivlan_id = response.json()["vid"]
            self.log.info('VLAN from Netbox: ', ivlan_id)
            vars.add('ivlan', ivlan_id)

            name = "L3VPN-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            self.log.info('Name: ', name)
            vars.add('pe_device', endpoint.pe_device)
            vars.add('cpe_interface_address', endpoint.cpe_interface.ipv4_address)
            self.log.info('cpe_interface_address: ', endpoint.cpe_interface.ipv4_address)
            vars.add('pe_interface_name', endpoint.pe_interface.interface_name)
            vars.add('pe_interface_number', endpoint.pe_interface.interface_number)
            pe_interface_description = "L3VPN interface to " + str(endpoint.cpe_device) + ", interface " + str(endpoint.cpe_interface.interface_name) + str(endpoint.cpe_interface.interface_number)
            vars.add('pe_interface_description', pe_interface_description)
            self.log.info('pe_interface_description: ', pe_interface_description)
            # vars.add('pe_ipv4_address', endpoint.pe_interface.ipv4_address)
            # vars.add('pe_ipv4_mask', endpoint.pe_interface.ipv4_mask)
            self.log.info('ipv4_mask: ', ipv4_mask)
            template.apply('l3vpn_qinq_pe-template', vars)


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_qinq_cfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
