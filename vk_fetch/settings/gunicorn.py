_startup_logger = None
_request_logger = None


def _log_info(msg):
    global _startup_logger
    import os
    import datetime
    import logging
    if _startup_logger is None:
        logger = logging.getLogger('startup')
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(ch)
        _startup_logger = logger
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S +0000')  # gunicorn's default format
    pid = os.getpid()
    output = '[%(time)s] [%(pid)s] [INFO] %(msg)s' % locals()
    _startup_logger.info(output)


def _log_request(msg):
    global _request_logger
    import logging
    if _request_logger is None:
        logger = logging.getLogger('server.requests')
        _request_logger = logger
    output = ' %(msg)s' % locals()
    _request_logger.info(output)


def _suppress_broken_pipe_error():
    """Monkey patch the handle_error() to not write a stacktrace on broken pipe.

    When browser reads from the socket and then decides that the resource being read didn't change,
    or when user reloads the document, then the browser may forcibly close the connection because it
    does not need more data. The other end of this socket (the python web server) now raises a socket
    exception telling the program that the client 'Broke the socket pipe'.
    """
    from gevent import hub

    orig_handle_error = hub.Hub.handle_error

    def patched_handle_error(self, context, type, value, tb):
        if str(value) == '[Errno 32] Broken pipe':
            if not issubclass(type, self.NOT_ERROR):
                del tb
                if context is not None:
                    raw_uri = 'Unknown'
                    request_method = ''
                    if not isinstance(context, str):
                        formatted_context = ''
                        try:
                            formatted_context = self.format_context(context)
                        except:
                            formatted_context = repr(context)
                        try:
                            raw_uri = context['RAW_URI']
                            request_method = context['REQUEST_METHOD']
                        except:
                            raw_uri = 'Undefined'
                    formatted_context = ''
                    msg = 'Client forcibly closed connection: %(request_method)s %(raw_uri)s' \
                          '%(formatted_context)s' % locals()
                    _log_request(msg)

            if context is None or issubclass(type, self.SYSTEM_ERROR):
                self.handle_system_error(type, value)
            return

        orig_handle_error(self, context, type, value, tb)

    hub.Hub.handle_error = patched_handle_error


def _patch_the_world():
    from sys import modules
    if 'threading' in modules:
        if 'pydevd' not in modules:
            # Do not exit in the debug mode
            message = 'fatal: threading module was loaded before gevent world patch.'
            print(message)
            _log_info(message)
            import sys
            sys.exit(-1001)

    from importlib import import_module
    import_module('gevent.monkey').patch_all()
    import_module('psycogreen.gevent').patch_psycopg()

    from socketio.sgunicorn import GeventSocketIOWorker
    GeventSocketIOWorker.resource = 'v1/socket.io'

    from socketio.virtsocket import Socket
    from socketio.server import SocketIOServer
    from socketio.sgunicorn import GeventSocketIOWorker

    # workaround according to gevent-socketio issue
    # https://github.com/abourget/gevent-socketio/issues/132
    def patched_get_socket(self, sessid=''):
        socket = self.sockets.get(sessid)

        if socket is None:
            socket = Socket(self, self.config)
            self.sockets[socket.sessid] = socket
        else:
            socket.incr_hits()

        return socket

    SocketIOServer.get_socket = patched_get_socket
    GeventSocketIOWorker.policy_server = False
    _suppress_broken_pipe_error()

    _log_info('Made the world green!')


_world_patched = False
if not _world_patched:
    # Importing the multiprocessing module causes to load the treading module. It's important to invoke
    # gevent.monkey.patch_all() before something gets the threading module loaded in order get green
    # world working well.
    # unicorn's app.base.py dynamically loads this file in the load_config() function during wsgiapp initialization.
    _world_patched = True
    _patch_the_world()
else:
    _log_info('World was already patched.')


import multiprocessing

bind = ["unix:///var/run/usercare/usercare.sock", "0.0.0.0:8000"]
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'socketio.sgunicorn.GeventSocketIOWorker'
max_requests = 7500


def post_worker_init(worker):
    """gunicorn calls this function just after a worker has initialized the application."""
    from server import ptrace
    ptrace.patch_world()
    from hashlib import sha1
    from os import getpid
    from time import time
    from socket import gethostname
    from server.core.signals import server_node_start
    my_name = '%s:%s:%s:%s' % (getpid(), gethostname(), bind, time())
    my_name_hash = sha1(my_name).hexdigest()
    server_node_start.send(sender=post_worker_init, node_id=my_name_hash)
    from socketio.server import SocketIOServer
    using_patched_worker = str(SocketIOServer.get_socket).endswith('.patched_get_socket>')
    if using_patched_worker:
        worker.log.info('post_worker_init: Worker is green.')
    else:
        worker.log.info('post_worker_init: CAUTION! Worker is not green! ')


def worker_exit(server, worker):
    """gunicorn calls this function when server stops a worker."""
    import sys
    try:
        server_node_stop = sys.modules['server.core.signals'].server_node_stop
        server_node_stop.send(sender=worker_exit)
    except KeyError:
        return
