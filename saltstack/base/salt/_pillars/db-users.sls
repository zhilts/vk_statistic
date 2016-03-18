#!jinja|yaml

{% if grains['platform'] in ["local","vbox","docker"] %}
db:
  users:
    root:
      pw: 3XFWvwJhyHD5tcAm
    monitor:
      pw: monitor
    user:
      pw: user123
    vagrant:
      pw: vagrant123
{% else %}

{% endif %}
