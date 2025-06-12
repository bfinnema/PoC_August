# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        vars.add('device', service.device)

        # BGP part
        bgp_rfs_name = f"BGP-INFRA-{service.device}"
        vars.add('bgp_rfs_name', bgp_rfs_name)
        vars.add('as_number', service.as_number)
        vars.add('bgp_router_id', service.loopback0_ipv4_address)
        vars.add('rr1_ipv4_address', service.rr1_ipv4_address)
        vars.add('rr2_ipv4_address', service.rr2_ipv4_address)
        template.apply('infra_pe_bgp-template', vars)

        # ISIS part
        net_id = "49.0002.{}.{}.{}.00".format(*[''.join(map(lambda x: x.zfill(3), service.loopback0_ipv4_address.split('.')))[i:i+4] for i in range(0, 12, 4)])
        vars.add('net_id', net_id)
        vars.add('loopback0_ipv4_address', service.loopback0_ipv4_address)
        vars.add('isis_process_id', service.isis_process_id)
        for interface in service.interfaces:
            isis_rfs_name = f"ISIS-INFRA-{service.device}-{interface.interface_number}"
            vars.add('isis_rfs_name', isis_rfs_name)
            mpls_rfs_name = f"MPLS-INFRA-{service.device}-{interface.interface_number}"
            vars.add('mpls_rfs_name', mpls_rfs_name)
            vars.add('interface_name', interface.interface_name)
            vars.add('interface_number', interface.interface_number)
            vars.add('ipv4_address', interface.ipv4_address)
            vars.add('ipv4_mask', interface.ipv4_mask)
            vars.add('interface_description', interface.interface_description)
            self.log.info('DOING ISIS: ', isis_rfs_name)
            template.apply('infra_pe_isis-template', vars)
            self.log.info('DOING MPLS: ', mpls_rfs_name)
            template.apply('infra_pe_mpls-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('infra_pe_cfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
