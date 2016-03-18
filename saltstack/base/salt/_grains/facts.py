#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: Daniel Kinon
"""

import logging
import subprocess

import salt.modules.file
import salt.modules.network

LOG = logging.getLogger(__name__)

__salt__ = {
    'cmd.run_all': salt.modules.cmdmod._run_all_quiet
}


# Initialize generic fact grains
def fact_grains():
    # Initialize Dictionary
    grains = { 'facts': {} }

    # Initialize shortcut grains
    grains['roles'] = []
    grains['environment'] = 'NA'
    grains['platform'] = 'NA'

    checkDmidecode = __runCommand("dmidecode -s system-product-name")
    if checkDmidecode == "VirtualBox":
      isVirtualBox = True
      grains['environment'] = "local-dev"
      grains['platform'] = "vbox"
      grains['roles'] = ['db', 'api']

    # Miscelaneous Facts
    grains['ssh_host_fingerprint'] = __runCommand("ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub | awk {'print $2'}")

    return grains

# Run Command
def __runCommand( command ):
  process = subprocess.Popen( command, stdout=subprocess.PIPE, shell=True )
  output = process.stdout.read().rstrip("\n\r")
  return output

