/etc/facts:
  file.directory:
    - mode: 755

/etc/facts/environment:
  file.managed:
    - template: jinja
    - source: salt://base/files/facts/environment
    - mode: 644
    - require:
      - file: /etc/facts
