vagrant:
  user:
    - present
    - home: /home/vagrant

/home/vagrant/.bashrc:
  file.managed:
#    - template: jinja
    - source: salt://users/files/bashrc/vagrant.sh
    - user: vagrant
    - group: vagrant
    - mode: 0600
    - require:
      - user: vagrant