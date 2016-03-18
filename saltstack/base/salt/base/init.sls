include:
  - .facts
{% if grains['environment'] != 'local-dev' %}
  - users.devops
  - users.engineering
  - collectd
  - .root-user
{% endif %}

## Hosts
/etc/hosts:
  file.managed:
    - template: jinja
    - source: salt://base/files/hosts
    - user: root
    - group: root
    - mode: 0644
    - order: 1

## Base Packages
base-pkgs:
  pkg.latest:
    - pkgs:
      - git
#      - screen
#      - net-tools
#      - nmap-ncat
#      - fio
#      - iptraf-ng
#      - perf
      - htop
#      - iotop
#      - wget
#      - psmisc

## Add SNI support to python-requests
python-sni-support:
  pkg.latest:
     - name: python-requests

## AWS Configuration
{% if grains['platform'] == 'aws' %}
python-boto:
  pkg.latest:
     - name: python-boto
     - order: 1

/root/.aws:
  file.directory:
    - makedirs: True
    - order: 1

/root/.aws/credentials:
  file.managed:
    - template: jinja
    - source: salt://base/files/aws-credentials
    - user: root
    - group: root
    - mode: 0644
    - order: 1
    - require:
      - file: /root/.aws
{% endif %}


### Shell Configs
#/root/.bashrc:
#  file.managed:
#    - source: salt://base/files/bashrc
#    - mode: 0755

#/root/.vimrc:
#  file.managed:
#    - source: salt://base/files/vimrc
#    - mode: 0755

/etc/profile.d/color-prompt.sh:
  file.managed:
    - source: salt://base/files/color-prompt.sh
    - mode: 0755



### resolv.conf
#{% from "base/map.jinja" import base with context %}
#/etc/resolv.conf:
#  file.managed:
#    - source: salt://base/files/resolv.conf
#    - template: jinja
#    - mode: 0644


## SELinux
/etc/selinux/config:
  file.managed:
    - source: salt://base/files/selinux-config

/usr/sbin/setenforce 0 || true:
  cmd.wait:
    - watch:
      - file: /etc/selinux/config


## sysctl
## make sure conntrack module is loaded
#modprobe ip_conntrack:
#  cmd.run:
#    - unless: lsmod | grep nf_conntrack
#
#{% for key,val in pillar['sysctl'].items() %}
#{{key}}:
#  sysctl.present:
#    - value: {{val}}
#{% endfor %}

# Add sysctl.d support to centos6
/etc/sysctl.d:
  file.directory:
    - mode: 0755

/usr/local/bin/sysctl-apply:
  file.managed:
    - source: salt://base/files/sysctl-apply.sh
    - user: root
    - group: root
    - mode: 0755

salt-minion:
  pkg.latest:
     - name: salt-minion
  service.running:
    - enable: True
    - require:
      - pkg: salt-minion


/etc/salt/minion.d/mine.conf:
  file.managed:
    - source: salt://base/files/salt-minion.d/mine.conf
    - user: root
    - group: root
    - mode: 0644
    - watch_in:
      - service: salt-minion

{% if 'db' in grains['roles'] %}
/etc/salt/minion.d/mysql.conf:
  file.managed:
    - source: salt://base/files/salt-minion.d/mysql.conf
    - user: root
    - group: root
    - mode: 0644
    - watch_in:
      - service: salt-minion
{% endif %}


# Sudoers
/etc/sudoers.d/wheel:
  file.managed:
    - source: salt://base/files/sudoers-wheel
    - user: root
    - group: root
    - mode: 0600

postfix:
  pkg.latest:
     - name: postfix
  service.running:
    - enable: True
    - require:
      - pkg: postfix

