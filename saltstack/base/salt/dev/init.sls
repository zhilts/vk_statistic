include:
  - app.api
  - users.vagrant


local-dev-pkgs:
  pkg:
    - latest
    - pkgs:
      - firefox
      - xvfb
      - fabric


python-pkgs:
  pkg.latest:
    - pkgs:
      - python-pip
      - python-dev

/etc/init.d/Xvfb:
  file.managed:
    - source: salt://dev/files/Xvfb.init
    - mode: 755

Xvfb-service:
  service.running:
    - name: Xvfb
    - enable: True
    - require:
      - file: /etc/init.d/Xvfb

/etc/profile.d/Xvfb.sh:
  file.managed:
    - source: salt://dev/files/Xvfb.profile
    - mode: 0755

