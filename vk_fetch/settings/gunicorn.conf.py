import multiprocessing

bind = ["unix:///usr/run/vk-fetch/api/api.sock", "0.0.0.0:8000"]
workers = multiprocessing.cpu_count() * 2 + 1
