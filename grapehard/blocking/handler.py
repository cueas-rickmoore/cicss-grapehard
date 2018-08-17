
from csftool.methods import CsfToolRequestHandlerMethods
from csftool.methods import CsfToolVarietyRequestHandlerMethods

from grapehard.factory import GrapeHardinessToolFactory
from grapehard.handler import GrapeHardinessRequestHandlerMethods

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from csftool.blocking.handler import CsfToolOptionsRequestHandler
GRAPEHARD_OPTIONS_HANDLER = CsfToolOptionsRequestHandler

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessBlockingRequestHandler(GrapeHardinessToolFactory,
                                           GrapeHardinessRequestHandlerMethods,
                                           CsfToolRequestHandlerMethods):

    def __init__(self, server_config, debug=False, **kwargs):
        # initialize the factory and it's inherited config/registry
        GrapeHardinessToolFactory.__init__(self, server_config.mode)
        # server config requirements for CsfToolRequestHandlerMethods
        self.setServerConfig(server_config)
        self.setToolConfig(server_config)
        # additional attributes required by specific request handlers
        if kwargs: self.setHandlerAttributes(self, **kwargs)

        self.debug = debug

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GrapeHardinessVarietyRequestHandler(GrapeHardinessToolFactory,
                                          GrapeHardinessRequestHandlerMethods,
                                          CsfToolVarietyRequestHandlerMethods):

    def __init__(self, server_config, debug=False, **kwargs):
        # initialize the factory and it's inherited config/registry
        GrapeHardinessToolFactory.__init__(self, server_config.mode)
        # server config requirements for CsfToolRequestHandlerMethods
        self.setServerConfig(server_config)
        self.setToolConfig(server_config)
        # additional attributes required by specific request handlers
        if kwargs: self.setHandlerAttributes(self, **kwargs)

        self.debug = debug

