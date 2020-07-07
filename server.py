import importlib
import json
import socket
import sys
import threading
import traceback

import maya.utils


def server_thread(host='127.0.0.1', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    while True:
        # Wait for a connection
        print >> sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()

        try:
            print >> sys.stderr, 'connection from', client_address
            _msg_size = int(connection.recv(8))
            print >> sys.stderr, 'receiving msg size "%s"' % _msg_size
            data = connection.recv(_msg_size)
            print >> sys.stderr, 'received "%s"' % data

            if data == 'kill':
                break

            module, method, args, kwargs = __extract_data(data)
            res = __call_method(module, method, args, kwargs)

            package = {'ok': 1, 'data': res}
            connection.sendall(json.dumps(package))

        except Exception as e:
            error = {'ok': 0,
                     'error_type': e.__class__.__name__,
                     'error_subject': str(e),
                     'error_string': traceback.format_exc()}
            connection.sendall(json.dumps(error))

        finally:
            # Clean up the connection
            connection.close()


def __call_method(module, method, args, kwargs):
    m = importlib.import_module(module)
    f = getattr(m, method)
    print 'calling method', m, f, args, kwargs
    res = maya.utils.executeInMainThreadWithResult(f, *args, **kwargs)
    return res


def __extract_data(data):
    data = json.loads(data)
    module = data['module']
    method = data['method']
    args = data['args']
    kwargs = data['kwargs']
    return module, method, args, kwargs


thread = threading.Thread(target=server_thread)
thread.start()
