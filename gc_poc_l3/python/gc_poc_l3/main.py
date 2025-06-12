# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import ipaddress

class ServiceCallbacks(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        # assert service.vrf_name in root.devices.device[service.link.pe.device].config.

        vars = ncs.template.Variables()
        template = ncs.template.Template(service)

        # vars.add('INDEX', 1)         # Used for the VRF configuration, but we assume VRF is present, so not used, really
        # vars.add('AS_NUMBER', "100")    # For test in the Cisco dksplab
        vars.add('AS_NUMBER', "31027")    # The real GC AS

        pe_if_name = "GigabitEthernet"
        interface_types = {"GigabitEthernet", "TenGigE", "TwentyFiveGigE", "HundredGigE"}
        for iftype in interface_types:
            if service.link.pe.interface.startswith(iftype):
                pe_if_name = iftype
                pe_if_number = service.link.pe.interface[len(iftype):]
        vars.add('PE_IF_NAME', pe_if_name)
        vars.add('PE_IF_NUMBER', pe_if_number)

        reserved_if_name = "TenGigE"
        vars.add('RESERVED_IF_NAME', reserved_if_name)
        vars.add('RESERVED_IF_NUMBER', pe_if_number)

        ip_prefix = service.link.pe.ipv4.ip_prefix
        self.log.info('Ip Prefix: ', ip_prefix)
        net_address = ipaddress.ip_network(ip_prefix)
        pe_if_address = net_address[0]
        ce_if_address = net_address[1]
        if_netmask = net_address.netmask
        if_cidrmask = ip_prefix.split("/")[1]
        self.log.info('PE interface address: ', pe_if_address)
        self.log.info('PE interface netmask: ', if_netmask)
        vars.add('PE_IF_IPV4', pe_if_address)
        vars.add('CE_IF_IPV4', ce_if_address)
        vars.add('PE_IF_MASK', if_netmask)
        vars.add('PE_IF_CIDR_MASK', if_cidrmask)
        self.log.info('PE interface CIDR netmask: ', if_cidrmask)

        acl_name = f"{service.underlay_id}-IPv4-RPF"
        vars.add('ACL_NAME', acl_name)
        pe_if_description = f"{service.underlay_id} - VRF: {service.vrf_name}"
        vars.add('PE_IF_DESCRIPTION', pe_if_description)
        reserved_if_description = f"Reserved {service.underlay_id}"
        vars.add('RESERVED_IF_DESCRIPTION', reserved_if_description)
        acl_description = f"# RFP IPv4 ACL - {service.underlay_id}"
        vars.add('ACL_DESCRIPTION', acl_description)
        bgp_neighbor_description = f"GlobalConnectAS BGP for {service.underlay_id} - {service.link.pe.interface}"
        vars.add('BGP_NEIGHBOR_DESCRIPTION', bgp_neighbor_description)
        
        vars.add('IF_SERVICE_POLICY_IN', f"PM-ACCESS-IN-INTERNET-{service.link.qos.bandwidth.upload}M")
        vars.add('IF_SERVICE_POLICY_OUT', f"PM-ACCESS-OUT-SCHD-NOQOS-{service.link.qos.bandwidth.download}M")

        vars.add('BGP_ROUTE_POLICY_IN', f"Internet-PRIVATE-AS-CUST-IPV4-IN(Inet-{service.underlay_id})")
        vars.add('PREFIX_SET_NAME', f"Inet-{service.underlay_id}")

        template.apply('gc_poc_l3-template', vars)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_service('gc_poc_l3-servicepoint', ServiceCallbacks)

    def teardown(self):
        self.log.info('Main FINISHED')
