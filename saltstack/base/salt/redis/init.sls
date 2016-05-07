#include:
#  - repos.uc-base

redis-server:
  pkg:
    - installed
  service.running:
    - enable: True
