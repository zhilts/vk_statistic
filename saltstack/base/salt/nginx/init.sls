nginx:
  pkg:
    - latest
  service:
    - running
    - enable: True
    - require:
      - pkg: nginx

# Replace stock nginx conf
/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/files/nginx.conf
    - template: jinja
    - mode: 644
    - watch_in:
      - service: nginx
