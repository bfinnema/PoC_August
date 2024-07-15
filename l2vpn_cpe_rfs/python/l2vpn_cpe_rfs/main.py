# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vlan_octet = service.ovlan % 256
        vars.add('vlan_octet', vlan_octet)
        self.log.info('VLAN Octet: ', vlan_octet)
        template = ncs.template.Template(service)
        template.apply('l2vpn_cpe_rfs-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l2vpn_cpe_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
