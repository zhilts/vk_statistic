{% set pgVer = '9.4' %}
{% set pgVerCompact = pgVer|replace('.','') %}
#include:
#  - repos.postgresql-{{ pgVerCompact }}

#postgresql-python:
#  pkg.latest:
#    - name:
#      - postgresql{{ pgVerCompact }}
##      - postgresql{{ pgVerCompact }}-python
#    - order: 1

#/etc/systemd/system/postgresql.service:
#  file.managed:
#    - template: jinja
#    - source: salt://postgresql/files/postgresql.service
#    - user: postgres
#    - group: postgres
#    - mode: 0644
#    - require:
#      - pkg: postgresql-server

/etc/postgres:
  file.directory:
    - makedirs: True

postgres-pkg:
  pkg.installed:
      - pkgs:
        - postgresql-{{pgVer}}
        - postgresql-server-dev-{{pgVer}}

/etc/postgres/conf.d:
  file.directory:
    - makedirs: True
    - require:
      - file: /etc/postgres

postgresql-server:
#  cmd.run:
#    - creates: /var/lib/pgsql/{{ pgVer }}/data/postgresql.conf
  service:
    - running
    - name: postgresql
    - enable: True
    - require:
      - file: /etc/postgres/conf.d
  postgres_user:
    - present
    - name: root
    - password: {{ pillar['db']['users']['root']['pw'] }}
    - superuser: True
    - require:
      - service: postgresql
  postgres_database:
    - present
    - name: root
  require:
    - pkg: postgres-pkg

/root/.pgpass:
  file.managed:
    - template: jinja
    - source: salt://postgresql/files/root-pgpass
    - user: root
    - group: root
    - mode: 600

{% for file in ['postgresql.conf','pg_hba.conf','pg_ident.conf'] %}
/etc/postgres/{{ file }}:
  file.symlink:
    - target: /etc/postgresql/{{ pgVer }}/main/{{ file }}
    - require:
      - file: /etc/postgres
      - service: postgresql-server
{% endfor %}

/etc/postgresql/{{ pgVer }}/main/postgresql.conf:
  file.managed:
    - source: salt://postgresql/files/postgresql-{{ pgVer }}.conf
    - user: postgres
    - group: postgres
    - mode: 600
    - require:
      - service: postgresql-server
#    - watch_in:
#      - service: postgresql

/etc/postgresql/{{ pgVer }}/main/pg_hba.conf:
  file.managed:
    - template: jinja
    - source: salt://postgresql/files/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: 600
    - require:
      - service: postgresql-server
#    - watch_in:
#      - service: postgresql

## Replication Configuration
{% if pillar['postgresql']['clusterMembers'][grains['fqdn']] is defined -%}
repl postgres account localhost:
  postgres_user.present:
    - name: repl
    - password: {{ pillar['db']['users']['repl']['pw'] }}
    - replication: True
    - login: True
    - require:
      - service: postgresql
repl postgres connlimit:
  module.run:
    - name: postgres.user_update
    - username: repl
    - connlimit: 1

{%- endif %}

vk-fetch postgres user:
  postgres_user:
    - present
    - name: user
    - password: {{ pillar['db']['users']['user']['pw'] }}
    - require:
      - service: postgresql

{% for db in ['vk-fetch'] %}
vk-fetch postgres db {{ db }}:
  postgres_database:
    - present
    - name: {{ db }}
    - owner: user
    - require:
      - service: postgresql
{% endfor %}

{% if grains['environment'] == 'local-dev' %}
vagrant postgres super user:
  postgres_user:
    - present
    - name: vagrant
    - password: {{ pillar['db']['users']['vagrant']['pw'] }}
    - superuser: True
    - require:
      - service: postgresql

vagrant postgres db:
  postgres_database:
    - present
    - name: vagrant
    - owner: vagrant
    - require:
      - service: postgresql
{% endif %}
