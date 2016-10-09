from settings.gevent_init import patch_world

patch_world()

import multiprocessing

bind = ["unix:///usr/run/vk-fetch/api/api.sock", "0.0.0.0:8000"]
workers = multiprocessing.cpu_count() * 2 + 1
