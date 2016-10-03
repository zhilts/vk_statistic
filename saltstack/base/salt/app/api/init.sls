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
      - gettext
      - python3.4
      - python-virtualenv
      - libpq-dev
      - gcc
      - python3-dev
      - libffi-dev

/usr/run/vk-fetch/api/releases:
  file.directory:
    - user: user
    - group: vk-fetch
    - mode: 0775
    - makedirs: True

{% if grains['environment'] != 'local-dev' %}
/etc/nginx/conf.d/api.conf:
  file.managed:
    - source: salt://app/api/files/api.conf
    - template: jinja
    - user: root
    - group: root
    - mode: 0644
    - watch_in:
      - service: nginx

/var/log/nginx/api:
  file.directory:
    - user: root
    - group: root
    - mode: 0755
    - makedirs: True

/etc/logrotate.d/nginx-agent:
  file.managed:
    - source: salt://app/api/files/agent.logrotate
    - user: root
    - group: root
    - mode: 0644
{% endif %}

/etc/supervisor/conf.d/api.ini:
  file.managed:
    - source: salt://app/api/files/supervisor.ini
    - template: jinja
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True

{% endif %}


{% for file in ['verify.html','karma-social.com.crt','karma-social.com.key'] %}
/etc/nginx/ssl/{{ file }}:
  file.managed:
    - source: salt://app/api/files/{{ file }}
    - user: root
    - group: root
    - mode: 0644
    - makedirs: True
{% endfor %}
