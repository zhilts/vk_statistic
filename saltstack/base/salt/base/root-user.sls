root ssh keys:
  ssh_auth.present:
    - user: root
    - names:
      - no-port-forwarding,no-agent-forwarding,no-X11-forwarding,command="echo 'Please login as the user \"centos\" rather than the user \"root\".';echo;sleep 10" ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCrmtGB/7HRvj1iWWGiYxhYc6Gfz6PdpyU/ooqMUshxmnmarfCkIJQv+fZj1KvG02o2lizCOIUInlRVIe9Bxo1RA3W60vGcXvi85UMkDLcGo9hC/LJRg/AbqmyXzszsyOXzniYRysQz/tf8KdrGInv7lKDkZNpFvZS8Aft8PiUz5L8saQUXsO5Fvuvyyz0dar+KMqVuAE6gNpSx6rwhqY0LU06L1/jtX6pkrumH8wyXV/F+nB7znTbQZBe7BhDKZ9lmTkv/RPL6s/5615/x2B5E1hVaLUi3CHU4h1mDSktqJQEFYwtXNsIIXPU9uSDJ8aRW9xRU7e658WDvRjBc4EJ5 default
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC7MNk3Dk+E+KkS1Z4f4CuovuKAvVp/yPs7mlrZydUsC8r/8NltlFhEb8C7YQwEOOt+IXVI+e8Cd/Sw/2H7qURvSycYl4bhl/wTrJM6Ff6I3i6M1q+r471rRYI+p3F4ADQeZHcKcLzdZBxd8cIbODeMZg3uu2UhEnnJKYG0FzDheabDvMEdWpl+HfYggbgOdAxEa3CRTS3MSr2Gxlvhk2+upvGffvd5xWqSxXMnW3uhVOZPCNZ0lGOLvFJ/4PVoj/S78cSeKfhtKld46RNsfKx7BLqjvMSKWq+JZePOjOuynA3xTMks4oVdNKxD5XlF/ZAsi2mGxe6kg0bAlprxtD0pgx75rV246uRBSxYKWy8VDmG/EJsAFMiozoWP/HHwzc00XT+YK4uVLO5VmysU7S2HrUMvTMKPhiPJz0C/dyzdlC0pQVYvUQRaRVGs+KA/pAQDVdvJhdNSDuUoEN6Hi8QYVh+x98WrthYetpMjloOrtmPE0X82q0qRq4ughDP3tmN9gl1+Wtq5B3rzv2fCcv3x8J15lc8IM1zdlisIRpUP+5RgefmTdZgYp8T+1Nvo9qdlulSYDlojBlJUqWcB6CpvjzGAPomr+T3ErGrzSEmuC7ikfktw4/2ilXc4h1DwzqAIi9bQ3BDgAHC8MeAvpXGT41JIBuLPsuxStXI8fDTTgw== root@admin.family-tree.int

{% for hostname, data in salt['mine.get']( '*', 'host.info' ).items() %}
{{ hostname }} root ssh_known_hosts:
  ssh_known_hosts:
    - present
    - user: root
    - name: {{ data['host'] }}
    - fingerprint: {{ data['ssh_host_fingerprint'] }}
{{ data['ip'] }} root ssh_known_hosts:
  ssh_known_hosts:
    - present
    - user: root
    - name: {{ data['ip'] }}
    - fingerprint: {{ data['ssh_host_fingerprint'] }}
{% endfor %}
