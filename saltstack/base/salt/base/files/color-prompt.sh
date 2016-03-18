#!/bin/bash

#### ASCII 16 Foreground Color ####
# Notes: http://misc.flogisoft.com/bash/tip_colors_and_formatting#foreground_text
DEFAULT="0;39m"
BLACK="0;30m"
RED="0;31m"
GREEN="0;32m"
YELLOW="0;33m"
BLUE="0;34m"
MAGENTA="0;35m"
CYAN="0;36m"
LGRAY="0;37m"
DGRAY="0;90m"
LRED="0;91m"
LGREEN="0;92m"
LYELLOW="0;93m"
LBLUE="0;94m"
LMAGENTA="0;95m"
LCYAN="0;96m"
WHITE="0;97m"

#### ASCII 256 Foreground Color ####
# Notes: http://misc.flogisoft.com/bash/tip_colors_and_formatting#foreground_text1
DORANGE="38;5;166m"
ORANGE="38;5;202m"
LORANGE="38;5;208m"
####################################

RESET="\[\e[0m\]"
COLOR="\[\e[${DEFAULT}\]"
ROOT="\[\e[${LRED}\]"

# Retrieve Environment Tag
ENVNAME=`cat /etc/facts/environment 2>/dev/null | tr '[:lower:]' '[:upper:]'`
if [ -z $ENVNAME ]; then
  ENVNAME='N/A'
fi

# Set Color Based on Environment
if [[ $ENVNAME =~ ^PROD ]]; then
  COLOR="\[\e[${LRED}\]"
elif [[ $ENVNAME =~ ^STAGING ]]; then
  COLOR="\[\e[${YELLOW}\]"
elif [[ $ENVNAME =~ ^MGMT ]]; then
  COLOR="\[\e[${LORANGE}\]"
elif [[ $ENVNAME =~ ^DEV ]]; then
  COLOR="\[\e[${LGREEN}\]"
elif [[ $ENVNAME =~ ^LOCAL ]]; then
  COLOR="\[\e[${LGREEN}\]"
fi

# Reset Prompt
if [ $(id -u) -eq 0 >/dev/null  2>&1 ]; then
  export PS1="${COLOR}[${ENVNAME}${RESET} ${ROOT}\u@\h \W${COLOR}]#${RESET} "  
else
  export PS1="${COLOR}[${ENVNAME}${RESET} \u@\h \W${COLOR}]#${RESET} "
fi
