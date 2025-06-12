# -*- mode: python; python-indent: 4 -*-
import ncs
import _ncs
import jwt
import time
import json
from ncs.application import Service
from ncs.dp import Action

def lookup_config():
    """Get shared secret and algorithm stored in NCS"""
    logger.debug("jwt-auth: Retrieving config data from NCS")
    with ncs.maapi.single_read_trans("admin", "system") as trans:
        m = ncs.maapi.Maapi()
        m.install_crypto_keys()
        root = ncs.maagic.get_root(trans)
        config = root.nso_example_jwt_auth__jwt_auth
        return (config.algorithm, _ncs.decrypt(config.secret))
    
# ---------------
# ACTIONS EXAMPLE
# ---------------
class JwtAuthGetToken(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        global logger
        logger = self.log
        logger.info('action name: ', name)
        (algo, secret) = lookup_config()
        maapi = ncs.maapi.Maapi()
        maapi.attach(trans.th)
        groups = maapi.get_authorization_info(maapi.get_my_user_session_id()).groups
        logger.info(f'User Name: {uinfo.username}, Groups:  {groups}')
        token = {   "sub": uinfo.username, 
                    "http://tail-f.com/ns/ncs-jwt":{
                        "groups": " ".join(groups),
                        "time": int(time.time())
                    }
                }
        encoded_jwt = jwt.encode(token, secret, algorithm=algo)
        logger.info(f'Token content: {json.dumps(token)}')
        output.token = encoded_jwt


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')


    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # When using actions, this is how we register them:
        #
        self.register_action('jwt-auth-get-token', JwtAuthGetToken)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
