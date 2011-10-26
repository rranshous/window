## import all the servers
from base_server import BaseServer
import glob
import os.path

# find the modules in the servers dir
module_names = [ os.path.basename(f)[:-3] for f in
                 glob.glob(os.path.dirname(__file__)+"/*.py") ]

# import the modules
modules = [__import__('servers.%s'%m) for m in module_names]

# find the server objects
server_classes = []
for module in modules:
    for attr in dir(module):
        o = getattr(module,attr)
        if issubclass(o,BaseServer):
            # add to local scope
            locals()[attr] = o

