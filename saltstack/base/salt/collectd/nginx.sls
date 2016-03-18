include:
  - collectd

/etc/collectd.d/nginx.conf:
  file.managed:
    - template: jinja
    - source: salt://collectd/files/nginx.conf
    - user: root
    - group: root
    - mode: 0644
    - require:
      - pkg: collectd
    - watch_in:
      - service: collectd

