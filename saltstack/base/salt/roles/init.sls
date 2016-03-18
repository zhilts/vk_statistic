include:
  - base
{% if grains['environment'] == 'local-dev' %}
  - dev
{% endif %}
{% if 'db' in grains['roles'] %}
  - postgresql
{% endif %}
{% if 'api' in grains['roles'] %}
  - app.api
{% endif %}