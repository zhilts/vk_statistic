vagrant:
  user:
    - present
    - home: /home/vagrant
    - groups:
      - wheel
      - vk-fetch

/home/vagrant/.bashrc:
  file.managed:
#    - template: jinja
    - source: salt://users/files/bashrc/vagrant.sh
    - user: vagrant
    - mode: 0600
    - require:
      - user: vagrant