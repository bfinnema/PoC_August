# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action


# ---------------
# ACTIONS EXAMPLE
# ---------------
class CheckAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('action name: ', name)
        suppress_positive = input.suppress_positive.exists()
        include_unset = input.include_unset.exists()
        with ncs.maapi.single_read_trans('admin', 'python') as t:
            location = ncs.maagic.get_node(t, kp)
            root = ncs.maagic.get_root(t)
            iter = root.devices.device

            name = location._parent._name
            if name == 'devices':
                iter =  root.devices.device
            elif name == 'profile':
                iter = ( device for device in root.devices.device if device.device_profile == location._parent.name )
            elif name == 'device-group':
                iter = ( root.devices.device[d] for d in location._parent.device_name )
            elif name == 'device':
                iter = [ location._parent ]

            def result(device, message, OK):
                res = output.result.create()
                res.device = device.name
                res.message = message
                res.OK = OK
                return res

            for device in iter:
                version_found = None
                if device.device_type.ne_type._name == 'cli':
                    version_found = device.platform.version
                elif hasattr(device.live_status, 'native') and hasattr(device.live_status.native, 'version'):
                    # IOS-XE netconf
                    version_found = device.live_status.native.version
                elif hasattr(device.live_status, 'platform_inventory'):
                    # IOS-XR netconf
                    version_found = device.live_status.platform_inventory.racks.rack['0'].attributes.basic_info.software_revision
                
                if version_found is None:
                    result(device, 'Could not determine software version', False)
                elif device.target_software.version is None:
                    if include_unset:
                        result(device, f'No target version set, device version: {version_found}', True)
                elif version_found == device.target_software.version:
                    if not suppress_positive:
                        result(device, None, True)
                else:
                    message = f'Target: {device.target_software.version} Found: {version_found}'
                    result(device, message, False)


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #


        # When using actions, this is how we register them:
        #
        self.register_action('target-version-check', CheckAction)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
