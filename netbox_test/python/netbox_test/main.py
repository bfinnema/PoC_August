# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
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

        api_url="https://10.101.180.45/api/ipam/prefixes/1/available-ips/"
        headers = {"Authorization":"Token e657404c0e1f57481ad0a06c293e8fe794e720ac", "Accept": "application/json", "Content-Type": "application/json"}
        body = {}

        response=requests.post(api_url, headers=headers, json=body, verify=False)
        self.log.info('Netbox response, IP address reservation: ', response.json())
        ipv4_cidr = response.json()["address"]
        self.log.info('CIDR from Netbox: ', ipv4_cidr)
        ipv4_address, ipv4_mask, ipv4_cidr_mask = cidr_to_netmask(ipv4_cidr)
        self.log.info('Address: ', ipv4_address)
        self.log.info('Net Mask: ', ipv4_mask)
        self.log.info('CIDR Mask: ', ipv4_cidr_mask)

        api_url="https://10.101.180.45/api/ipam/vlan-groups/1/available-vlans/"
        body = {"name": service.ovlan_name}

        response=requests.post(api_url, headers=headers, json=body, verify=False)
        self.log.info('Netbox response, VLAN reservation: ', response.json())
        vlan_id = response.json()["vid"]
        self.log.info('VLAN from Netbox: ', vlan_id)

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)
        template.apply('netbox_test-template', vars)

class ReleaseResources(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('action name: ', name)
        self.log.info('KICKER HAS BEEN KICKED')
        self.log.info(f'Action input: kicker-id: {input.kicker_id}, path: {input.path}, tid: {input.tid}')
        self.log.info(dir(input))

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('netbox_test-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
