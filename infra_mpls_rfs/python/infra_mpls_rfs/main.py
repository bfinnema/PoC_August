# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        """ vars.add('DEVICE', service.device)
        vars.add('ROUTER_ID', service.router_id)
        vars.add('INTERFACE_NAME', service.interface_name)
        vars.add('INTERFACE_NUMBER', service.interface_number) """
        template = ncs.template.Template(service)
        template.apply('infra_mpls_rfs-template', vars)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('infra_mpls_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
