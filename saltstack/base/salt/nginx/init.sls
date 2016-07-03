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

#/etc/pki/tls/certs/vk-fetch.crt:
#  file.managed:
#    - source: salt://nginx/files/certs/vk-fetch.crt
#    - mode: 644
#    - parent: True
#    - watch_in:
#      - service: nginx

{% for file in ['certs/vk-fetch.crt', 'private/vk-fetch.key'] %}
/etc/pki/tls/{{file}}:
  file.managed:
    - source: salt://nginx/files/{{file}}
    - mode: 644
    - makedirs: True
    - watch_in:
      - service: nginx
{% endfor %}
