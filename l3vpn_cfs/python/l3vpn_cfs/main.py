# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
from datetime import datetime
import json
import ipaddress

class PingTest(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('action name: ', name)
        results = {}
        with ncs.maapi.single_read_trans('admin', 'python') as t:
            service = ncs.maagic.get_node(t, kp)
            root = ncs.maagic.get_root(t)
            for endpoint in service.endpoint:
                local_pe = endpoint.pe_device
                remote_result = None
                local_result = self.ping(root.devices.device[local_pe],
                                                          endpoint.cpe_loopback0_address, service.vrf_name)
                for remote in service.endpoint:
                    if remote.pe_device != local_pe:
                        remote_result = self.ping(root.devices.device[remote.pe_device],
                                                          endpoint.cpe_loopback0_address, service.vrf_name)  
                        break
                if remote_result is None:
                    remote_result = 'No remote PE to test from'                      
                results[endpoint.id] = { 'local': local_result, 'remote': remote_result}
        now = datetime.now()
        
        with ncs.maapi.single_write_trans('admin', 'python') as t:
            service = ncs.maagic.get_node(t, kp)
            service.last_ping.when = str(now)
            del service.last_ping.endpoint
            for endpoint in service.endpoint: 
                last_ping_endpoint = service.last_ping.endpoint.create(endpoint.id)
                last_ping_endpoint.local_result = results[endpoint.id]['local']
                last_ping_endpoint.remote_result = results[endpoint.id]['remote']           
            t.apply()
        output.result = json.dumps(results)

    def ping(self, pe, address, vrf):
            if 'iosxr' not in pe.device_type.netconf.ned_id:
                return "ERROR: Ping only supported on IOSXR with netconf NED"
            self.log.info(f'PING from device: {pe.name} to address: {address} in vrf: {vrf}')
            ping_action = pe.rpc.rpc_ping.ping
            ping_input = ping_action.get_input()
            dest = ping_input.destination.create()
            dest.destination = address
            dest.vrf_name = vrf
            ping_output_list = ping_action(ping_input).ping_response.ipv4
            self.log.info(repr(ping_output_list))
            for ping_output in ping_output_list:
                replies = ''.join((reply.result for reply in ping_output.replies.reply))
                # only one element in list
                return f'{pe.name} -> {address} :: {ping_output.success_rate}% success rate, replies: {replies}'


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
            vars.add('pe_interface_name', endpoint.pe_interface.interface_name)
            vars.add('pe_interface_number', endpoint.pe_interface.interface_number)
            pe_interface_description = "L3VPN interface to " + str(endpoint.cpe_device) + ", interface " + str(endpoint.cpe_interface.interface_name) + str(endpoint.cpe_interface.interface_number)
            vars.add('pe_interface_description', pe_interface_description)
            pe_ipv4_address = format(list(ipaddress.ip_network(endpoint.link_subnet).hosts())[0])
            self.log.info('PE IPv4 address: ', pe_ipv4_address)
            vars.add('pe_ipv4_address', pe_ipv4_address)
            ipv4_mask = format(ipaddress.ip_network(endpoint.link_subnet).netmask)
            self.log.info('PE IPv4 mask: ', ipv4_mask)
            vars.add('pe_ipv4_mask', ipv4_mask)
            cpe_ipv4_address = format(list(ipaddress.ip_network(endpoint.link_subnet).hosts())[1])
            vars.add('cpe_interface_address', cpe_ipv4_address)
            # vars.add('pe_ipv4_address', endpoint.pe_interface.ipv4_address)
            # vars.add('pe_ipv4_mask', endpoint.pe_interface.ipv4_mask)
            vars.add('vlan_id', endpoint.vlan_id)
            template.apply('l3vpn_pe-template', vars)

            # CPE part
            name = "L3VPN-"+str(endpoint.cpe_device)+"-"+str(endpoint.id)
            vars.add('name', name)
            vars.add('cpe_device', endpoint.cpe_device)
            # vars.add('remote_as_number', endpoint.as_number)
            # vars.add('as_number', endpoint.customer_as_number)
            vars.add('pe_interface_address', pe_ipv4_address)
            vars.add('cpe_loopback0_address', endpoint.cpe_loopback0_address)
            vars.add('cpe_loopback0_mask', '255.255.255.255')
            vars.add('cpe_interface_name', endpoint.cpe_interface.interface_name)
            vars.add('cpe_interface_number', endpoint.cpe_interface.interface_number)
            cpe_interface_description = "L3VPN interface to " + str(endpoint.pe_device) + ", interface " + str(endpoint.pe_interface.interface_name) + str(endpoint.pe_interface.interface_number)
            vars.add('cpe_interface_description', cpe_interface_description)
            self.log.info('CPE IPv4 address: ', cpe_ipv4_address)
            vars.add('cpe_ipv4_address', cpe_ipv4_address)
            vars.add('pe_ipv4_mask', ipv4_mask)
            # vars.add('cpe_ipv4_address', endpoint.cpe_interface.ipv4_address)
            # vars.add('cpe_ipv4_mask', endpoint.cpe_interface.ipv4_mask)
            template.apply('l3vpn_cpe-template', vars)

            if endpoint.qos.enable_qos_policy:
                pe_bit_rate = endpoint.qos.bit_rate
                cpe_bit_rate = 1000 * int(endpoint.qos.bit_rate)
                vars.add('pe_bit_rate', pe_bit_rate)
                vars.add('cpe_bit_rate', cpe_bit_rate)
                name = "L3VPN-QoS-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
                vars.add('name', name)
                template.apply('l3vpn_pe_qos-template', vars)
                name = "L3VPN-QoS-"+str(endpoint.cpe_device)+"-"+str(endpoint.id)
                vars.add('name', name)
                template.apply('l3vpn_cpe_qos-template', vars)
            
            if endpoint.acl.enable_acl:
                vars.add('acl_name', endpoint.acl.acl_name)
                name = "L3VPN-ACL-"+str(endpoint.pe_device)+"-"+str(endpoint.id)
                vars.add('name', name)
                template.apply('l3vpn_pe_acl-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_cfs-servicepoint', ServiceCallbacks)
        self.register_action('l3vpn_cfs-ping-test', PingTest)

    def teardown(self):
        self.log.info('Main FINISHED')
