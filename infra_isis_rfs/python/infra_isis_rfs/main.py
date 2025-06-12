# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add('DEVICE', service.device)
        vars.add('LOOPBACK0_IPV4_ADDRESS', service.loopback0_ipv4_address)
        vars.add('LOOPBACK0_IPV4_MASK', '255.255.255.255')
        vars.add('NET_ID', service.net_id)
        vars.add('ISIS_PROCESS_ID', service.isis_process_id)
        vars.add('INTERFACE_NAME', service.interface.interface_name)
        vars.add('INTERFACE_NUMBER', service.interface.interface_number)
        vars.add('IPV4_ADDRESS', service.interface.ipv4_address)
        vars.add('IPV4_MASK', service.interface.ipv4_mask)
        vars.add('INTERFACE_DESCRIPTION', service.interface.interface_description)
        template = ncs.template.Template(service)
        template.apply('infra_isis_rfs-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('infra_isis_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
