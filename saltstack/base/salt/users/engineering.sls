{% for user in pillar['ssh_users']['engineering'] %}
{{user}}:
  user:
    - present
    - shell: /bin/bash
    - home: /home/{{user}}
    - empty_password: True
    - groups:
      - wheel
      - family-tree
  file:
    - directory
    - name: /home/{{user}}
    - user: {{user}}
    - mode: 700
    - makedirs: True
    - require:
      - user: {{user}}
  ssh_auth:
    - present
    - user: {{user}}
    - source: salt://users/files/keys/{{user}}.pub
  ssh_known_hosts:
    - present
    - name: github.com
    - user: {{user}}
    - fingerprint: 16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48
{% endfor %}
