import json
import socket
import sys


class MayaModule(object):
    def __init__(self, name, host='127.0.0.1', port=12345):
        self.name = name
        self.host = host
        self.port = port

    def __getattr__(self, item):
        return MayaModuleMethod(self, item)

    def send(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall('%08d' % len(data))
        s.sendall(data)

        data = ''
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk

        if not data:
            return

        result = json.loads(data)
        if result['ok']:
            return result['data']
        else:
            # err_type = result['error_type']
            # err_subject = result['error_subject']
            err_string = result['error_string']
            print >> sys.stderr, err_string
            raise Exception('Maya Error')


class MayaModuleMethod(object):
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def __call__(self, *args, **kwargs):
        data = self.__build_data(*args, **kwargs)
        return self.__send(data)

    def __build_data(self, *args, **kwargs):
        return {
            'module': self.module.name,
            'method': self.name,
            'args': args,
            'kwargs': kwargs,
        }

    def __send(self, data):
        serialized = json.dumps(data)
        return self.module.send(serialized)


try:
    import maya.cmds as cmds
    import maya.utils as utils
except ImportError:
    cmds = MayaModule('maya.cmds')
    utils = MayaModule('maya.utils')

# cmds.send('kill')  # Kill Maya service so it can be restarted if necessary
