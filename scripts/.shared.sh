#!/usr/bin/env bash
# vim: ft=bash

set -e

# colors for extravagance
export bldgrn='\e[1;32m' # Green
export bldylw='\e[1;33m' # Yellow
export bldblu='\e[1;34m' # Blu
export clr='\e[0m'       # Text Reset

function puts() {
    printf ">>> ${bldgrn}$1 ${bldylw}${2}${clr} %s\n" "$3 $4 $5 $6"
}
