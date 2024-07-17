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

        vars = ncs.template.Variables()

        def cidr_to_netmask(cidr):
            network, net_bits = cidr.split('/')
            host_bits = 32 - int(net_bits)
            netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
            return network, netmask, net_bits

        headers = {"Authorization":"Token e657404c0e1f57481ad0a06c293e8fe794e720ac", "Accept": "application/json", "Content-Type": "application/json"}
        body = {}
        # api_url="https://10.101.180.45:8000/api/ipam/prefixes/1/available-ips/"
        api_url=f"https://{service.netbox_address}:{service.netbox_port}/api/ipam/prefixes/{service.netbox_ipv4_pool}/available-ips/"

        try:
            response=requests.post(api_url, headers=headers, json=body, verify=False)
            self.log.info('Netbox response, IP address reservation: ', response.json())
            ipv4_cidr = response.json()["address"]
            ipv4_reservation = response.json()["id"]
            self.log.info('CIDR from Netbox: ', ipv4_cidr)
            self.log.info('Netbox reservation number: ', ipv4_reservation)
            ipv4_address, ipv4_mask, ipv4_cidr_mask = cidr_to_netmask(ipv4_cidr)
            vars.add('ipv4_address', ipv4_address)
            vars.add('ipv4_mask', ipv4_mask)
            vars.add('ipv4_reservation', ipv4_reservation)
            template = ncs.template.Template(service)
            template.apply('section_33-template', vars)
        except:
            ipv4_cidr = "10.10.10.10/8"
            ipv4_address, ipv4_mask, ipv4_cidr_mask = cidr_to_netmask(ipv4_cidr)
            vars.add('pe_ipv4_address', ipv4_address)
            vars.add('pe_ipv4_mask', ipv4_mask)

        self.log.info('Address: ', ipv4_address)
        self.log.info('Net Mask: ', ipv4_mask)
        self.log.info('CIDR Mask: ', ipv4_cidr_mask)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('section_33-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
