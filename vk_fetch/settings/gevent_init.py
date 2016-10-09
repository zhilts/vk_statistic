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


def _patch_the_world():

    from importlib import import_module
    import_module('gevent.monkey').patch_all()
    import_module('psycogreen.gevent').patch_psycopg()

    _log_info('Made the world green!')


_world_patched = False


def patch_world():
    global _world_patched
    if not _world_patched:
        # Importing the multiprocessing module causes to load the treading module. It's important to invoke
        # gevent.monkey.patch_all() before something gets the threading module loaded in order get green
        # world working well.
        # unicorn's app.base.py dynamically loads this file in the load_config() function during wsgiapp initialization.
        _world_patched = True
        _patch_the_world()
    else:
        _log_info('World was already patched.')
