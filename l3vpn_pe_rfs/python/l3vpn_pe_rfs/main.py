# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        def netmask_to_cidr(m_netmask):
            return(sum([ bin(int(bits)).count("1") for bits in m_netmask.split(".") ]))

        vars = ncs.template.Variables()
        vars.add('LOOPBACK_IF_NUMBER', '0')
        vars.add('LOOPBACK_IP_ADDR', '2.2.2.2')
        vars.add('IPV4_CIDR', netmask_to_cidr(service.interface.ipv4_mask))

        template = ncs.template.Template(service)
        template.apply('l3vpn_pe_rfs-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_pe_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
