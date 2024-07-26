# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        vars.add('acl_name', service.acl_name)
        vars.add('source_ipv4_addr', "1.2.3.4")
        vars.add('source_prefix_length', 24)
        vars.add('dest_ipv4_addr', "4.3.2.1")
        vars.add('dest_prefix_length', 24)
        vars.add('source_scope', "any")
        vars.add('dest_scope', "any")
        for seq in root.inventory.access_lists.access_list[service.acl_name].sequence:
            vars.add('sequence_number', seq.sequence_number)
            # self.log.info('sequence number: ', seq.sequence_number)
            vars.add('permit_or_deny', seq.permit_or_deny)
            # self.log.info('permit_or_deny: ', seq.permit_or_deny)
            vars.add('protocol', seq.protocol)
            # self.log.info('protocol: ', seq.protocol)
            for statement in seq.statements:
                subject = statement.subject
                vars.add('subject', subject)
                # self.log.info('subject: ', subject)
                scope = statement.scope
                # self.log.info('scope: ', scope)
                if subject == "source":
                    vars.add('source_scope', scope)
                    if scope != "any":
                        vars.add('source_ipv4_addr', statement.ipv4_addr)
                        # self.log.info('source_ipv4_addr: ', statement.ipv4_addr)
                        if scope == "address":
                            vars.add('source_prefix_length', statement.prefix_length)
                            # self.log.info('source_prefix_length: ', statement.prefix_length)
                else:
                    vars.add('dest_scope', scope)
                    if scope != "any":
                        vars.add('dest_ipv4_addr', statement.ipv4_addr)
                        # self.log.info('dest_ipv4_addr: ', statement.ipv4_addr)
                        if scope == "address":
                            vars.add('dest_prefix_length', statement.prefix_length)
                            # self.log.info('dest_prefix_length: ', statement.prefix_length)
            vars.add('device', service.device)
            template.apply('l3vpn_pe_acl_rfs-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('l3vpn_pe_acl_rfs-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
