supervisor:
  pkg:
    - latest
  service:
    - name: supervisor
    - running
    - enable: True
    - require:
      - pkg: supervisor

# Make supervisor sock accessible by user
/var/run/supervisor:
  file.directory:
    - user: user
    - group: user
    - mode: 0770
    - makedirs: True
    - require:
      - user: user

# Replace stock supervisord.conf
/etc/supervisord.conf:
  file.managed:
    - source: salt://supervisor/files/supervisord.conf
    - template: jinja
    - mode: 0644
    - watch_in:
      - service: nginx
