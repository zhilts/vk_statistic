user:
  user:
    - present
    - shell: /bin/bash
    - home: /home/user
    - empty_password: True
  file.directory:
    - name: /home/user
    - user: user
    - group: user
    - mode: 0755
    - makedirs: True
    - require:
      - user: user

/home/user/.ssh:
  file.directory:
    - name: /home/user/.ssh
    - user: user
    - group: user
    - mode: 0700
    - makedirs: True
    - require:
      - user: user

/var/run/user:
  file.directory:
    - user: user
    - group: user
    - mode: 0755
    - makedirs: True
    - require:
      - user: user

/home/user/.ssh/authorized_keys:
  file.managed:
    - source: salt://users/files/authorized_keys/user
    - user: user
    - group: user
    - mode: 0600
    - require:
      - user: user


{%   if 'api' in grains['roles'] %}
/var/log/user:
  file.directory:
    - user: root
    - group: root
    - mode: 0755
    - makedirs: True

/etc/security/limits.d/user.conf:
  file.managed:
    - source: salt://users/files/limits.d/user.conf
    - user: root
    - group: root
    - mode: 0644

/home/user/.pgpass:
  file.managed:
    - template: jinja
    - source: salt://postgresql/files/user-pgpass
    - user: user
    - group: user
    - mode: 0600
    - require:
      - user: user

/home/user/supervisor:
  file.directory:
    - user: user
    - group: user
    - mode: 0755
    - makedirs: True
    - require:
      - user: user
{% endif %}

github.com:
  ssh_known_hosts:
    - present
    - user: user
    - fingerprint: 16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48
