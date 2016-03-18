#!/bin/sh

WORKINGDIR=$( dirname "${BASH_SOURCE[0]}" )
passwdFile=sasl_passwd

postmap -v hash:$WORKINGDIR/$passwdFile
