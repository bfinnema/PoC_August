# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add('DEVICE', service.device)
        vars.add('BGP_AS', service.as_number)
        vars.add('BGP_ROUTER_ID', service.bgp_router_id)
        vars.add('RR1_IPV4_ADDRESS', service.rr1_ipv4_address)
        vars.add('RR2_IPV4_ADDRESS', service.rr2_ipv4_address)
        template = ncs.template.Template(service)
        template.apply('infra_bgp_rfs-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('infra_bgp_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
