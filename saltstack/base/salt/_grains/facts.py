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
    grains = {'facts': {}}
    # Initialize shortcut grains
    grains['roles'] = []
    grains['environment'] = 'NA'
    grains['platform'] = 'NA'
    checkDmidecode = __runCommand("dmidecode -s system-product-name")
    if checkDmidecode == "VirtualBox":
        isVirtualBox = True
        grains['environment'] = "local-dev"
        grains['platform'] = "vbox"
        grains['roles'] = ['db', 'api', 'redis']

    isAWS=False
    checkAWS = __runCommand("head -c 3 /sys/hypervisor/uuid 2>/dev/null")
    if checkAWS == "ec2":
        isAWS = True
        grains['platform'] = "aws"
    # Handle AWS Specific Facts
    if isAWS:
        # Gather basic ec2 info
        grains['facts']['aws'] = {}
        grains['facts']['aws']['id'] = __runCommand("ec2metadata --instance-id")
        grains['facts']['aws']['type'] = __runCommand("ec2metadata --instance-type")
        grains['facts']['aws']['availability_zone'] = __runCommand("ec2metadata --availability-zone")
        grains['facts']['aws']['region'] = (grains['facts']['aws']['availability_zone'])[:-1]
        # Gather and process facts
        grains['facts']['aws']['tags'] = __getTags(grains['facts']['aws']['id'], grains['facts']['aws']['region'])
        # Create grain shortcuts
        if isinstance(grains['facts']['aws']['tags'], dict) and 'role' in grains['facts']['aws']['tags']:
            grains['roles'] = grains['facts']['aws']['tags']['role']
        if isinstance(grains['facts']['aws']['tags'], dict) and 'environment' in grains['facts']['aws']['tags']:
            grains['environment'] = grains['facts']['aws']['tags']['environment']
    # Miscelaneous Facts
    grains['ssh_host_fingerprint'] = __runCommand("ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub | awk {'print $2'}")
    return grains


def __getTags(myInstId, region):
    import boto.ec2
    ec2 = boto.ec2.connect_to_region(region)
    reservations = ec2.get_all_instances()
    for res in reservations:
        for inst in res.instances:
            if myInstId == inst.id:
                if inst.tags:
                    tags = dict((k.lower(), v.lower()) for k, v in inst.tags.iteritems())
                    # print "%s (%s) [%s] %s" % (inst.tags['Name'], inst.id, inst.state, inst.tags['Role'])
                    if 'role' in tags:
                        roles = tags['role'].split(',')
                        tags['role'] = roles
                    return tags
    return {}


# Run Command
def __runCommand(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output = process.stdout.read().rstrip("\n\r")
    return output
