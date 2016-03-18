#!jinja|yaml

ssh_users:
  engineering:
    - sergey.zhiltsov
    - anna.djachenko

sysctl:
  fs.file-max: 20000000
  net.core.netdev_max_backlog: 65536
  net.core.optmem_max: 25165824
  net.core.rmem_default: 1048576
  net.core.rmem_max: 16777216
  net.core.somaxconn: 65536
  net.core.wmem_default: 1048576
  net.core.wmem_max: 16777216
  net.ipv4.ip_local_port_range: "2000 65500"
  net.ipv4.tcp_timestamps: 0
  net.ipv4.tcp_fin_timeout: 20
  net.ipv4.tcp_keepalive_intvl: 5
  net.ipv4.tcp_keepalive_probes: 9
  net.ipv4.tcp_keepalive_time: 20
  net.ipv4.tcp_max_orphans: 500000
  net.ipv4.tcp_max_syn_backlog: 65536
  net.ipv4.tcp_rmem: "4096 87380 67108864"
  net.ipv4.tcp_tw_reuse: 0
  net.ipv4.tcp_tw_recycle: 0
  net.ipv4.tcp_wmem: "4096 87380 67108864"
  net.ipv6.conf.all.disable_ipv6: 1
  net.ipv6.conf.default.disable_ipv6: 1
  net.netfilter.nf_conntrack_max: 2000000
  net.netfilter.nf_conntrack_generic_timeout: 60
  net.netfilter.nf_conntrack_tcp_timeout_established: 86400
  net.netfilter.nf_conntrack_tcp_timeout_unacknowledged: 30
  net.ipv4.ip_forward: 0
  net.ipv4.conf.default.rp_filter: 1
  net.ipv4.conf.default.accept_source_route: 0
  kernel.sysrq: 0
  kernel.core_uses_pid: 1
#  net.ipv4.tcp_syncookies: 0
  net.ipv4.tcp_syncookies: 1
  kernel.msgmnb: 65536
  kernel.msgmax: 65536
  kernel.shmmax: 68719476736
  kernel.shmall: 4294967296
  net.ipv4.tcp_synack_retries: 2
#  vm.swappiness: 0
#  vm.overcommit_memory: 1
#  vm.overcommit_ratio: 1
