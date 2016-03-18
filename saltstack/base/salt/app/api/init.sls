{% if 'api' in grains['roles'] %}

include:
  - base
  - users.user
  - nginx
  - supervisor

agent-pkgs:
  pkg:
    - latest
    - pkgs:
      - python3.4
      - python-virtualenv
      - gcc
      - python3-dev

{% if grains['environment'] != 'local-dev' %}
/etc/nginx/conf.d/agent.conf:
  file.managed:
    - source: salt://app/api/files/api.conf
    - template: jinja
    - user: root
    - group: root
    - mode: 0644
    - watch_in:
      - service: nginx

/var/log/nginx/agent:
  file.directory:
    - user: root
    - group: root
    - mode: 0755
    - makedirs: True

/etc/logrotate.d/nginx-agent:
  file.managed:
    - source: salt://app/agent/files/agent.logrotate
    - user: root
    - group: root
    - mode: 0644
{% endif %}

/etc/supervisord.d/api.ini:
  file.managed:
    - source: salt://app/api/files/supervisor.ini
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True

/var/log/user/api:
  file.symlink:
    - target: /home/user/logs

{% endif %}
