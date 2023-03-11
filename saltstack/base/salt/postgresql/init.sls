{% set pgVer = '9.4' %}
{% set pgVerCompact = pgVer|replace('.','') %}

/etc/postgres:
  file.directory:
    - makedirs: True

# for ubuntu 14.04
postgress_repo:
  pkgrepo.managed:
    - humanname: Postgres 9.4 for ubuntu 14.04
    - name: deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main
    - gpgcheck: 1
    - key_url: https://www.postgresql.org/media/keys/ACCC4CF8.asc

postgres-pkg:
  pkg.installed:
      - pkgs:
        - postgresql-{{pgVer}}
        - postgresql-server-dev-{{pgVer}}
  require:
    - pkgrepo: postgress_repo

/etc/postgres/conf.d:
  file.directory:
    - makedirs: True
    - require:
      - file: /etc/postgres

postgresql-server:
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
    - createdb: True
    - require:
      - service: postgresql

{% for db in ['vk-fetch'] %}
database:
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
