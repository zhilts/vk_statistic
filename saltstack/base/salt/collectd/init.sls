include:
  - base
  - users.user

collectd:
  pkg:
    - latest
    - pkgs:
      - collectd
  service:
    - running
    - name: collectd
    - enable: True
    - require:
      - pkg: collectd

/etc/collectd.d/default.conf:
  file.managed:
    - template: jinja
    - source: salt://collectd/files/default.conf
    - user: root
    - group: root
    - mode: 0644
    - require:
      - pkg: collectd
    - watch_in:
      - service: collectd

