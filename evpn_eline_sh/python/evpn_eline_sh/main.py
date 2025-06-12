# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service

class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        #Common variables:
        vars.add('evpn_name', service.evpn_name)
        vars.add('evi_id', service.evi_id)

        # PE A:
        vars.add('vlan_id', service.pe_a_device.vlan_id)
        vars.add('source_ac_id', service.ac1_id)
        vars.add('remote_ac_id', service.ac2_id)
        self.log.info('PE A Device: ', service.pe_a_device.device)
        vars.add('device', service.pe_a_device.device)
        vars.add('interface_name', service.pe_a_device.interface.interface_name)
        vars.add('interface_number', service.pe_a_device.interface.interface_number)
        pe_interface_description = "To " + str(service.ce_a_device.device) + ", interface " + str(service.ce_a_device.interface.interface_name) + str(service.ce_a_device.interface.interface_number)
        vars.add('interface_description', pe_interface_description)
        pe_subinterface_description = "EVPN ELINE service: " + str(service.evpn_name)
        vars.add('subinterface_description', pe_subinterface_description)
        template.apply('evpn_eline_sh_pe-template', vars)

        # PE B:
        vars.add('vlan_id', service.pe_z_device.vlan_id)
        vars.add('source_ac_id', service.ac2_id)
        vars.add('remote_ac_id', service.ac1_id)
        self.log.info('PE Z Device: ', service.pe_z_device.device)
        vars.add('device', service.pe_z_device.device)
        vars.add('interface_name', service.pe_z_device.interface.interface_name)
        vars.add('interface_number', service.pe_z_device.interface.interface_number)
        pe_interface_description = "To " + str(service.ce_z_device.device) + ", interface " + str(service.ce_z_device.interface.interface_name) + str(service.ce_z_device.interface.interface_number)
        vars.add('interface_description', pe_interface_description)
        pe_subinterface_description = "EVPN ELINE service: " + str(service.evpn_name)
        vars.add('subinterface_description', pe_subinterface_description)
        template.apply('evpn_eline_sh_pe-template', vars)

        # CE A:
        self.log.info('CE A Device: ', service.ce_a_device.device)
        vars.add('device', service.ce_a_device.device)
        vars.add('interface_number', service.ce_a_device.interface.interface_number)
        vars.add('ipv4_address', service.ce_a_device.interface.ipv4_address)
        vars.add('ipv4_mask', service.ce_a_device.interface.ipv4_mask)
        ce_interface_description = "To " + str(service.pe_a_device.device) + ", interface " + str(service.pe_a_device.interface.interface_name) + str(service.pe_a_device.interface.interface_number)
        vars.add('interface_description', ce_interface_description)
        ce_subinterface_description = "EVPN ELINE service: " + str(service.evpn_name)
        vars.add('subinterface_description', ce_subinterface_description)
        template.apply('evpn_eline_sh_ce-template', vars)

        # CE B:
        self.log.info('CE Z Device: ', service.ce_z_device.device)
        vars.add('device', service.ce_z_device.device)
        vars.add('interface_number', service.ce_z_device.interface.interface_number)
        vars.add('ipv4_address', service.ce_z_device.interface.ipv4_address)
        vars.add('ipv4_mask', service.ce_z_device.interface.ipv4_mask)
        ce_interface_description = "To " + str(service.pe_z_device.device) + ", interface " + str(service.pe_z_device.interface.interface_name) + str(service.pe_z_device.interface.interface_number)
        vars.add('interface_description', ce_interface_description)
        ce_subinterface_description = "EVPN ELINE service: " + str(service.evpn_name)
        vars.add('subinterface_description', ce_subinterface_description)
        template.apply('evpn_eline_sh_ce-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('evpn_eline_sh-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
