#!/bin/bashh

command="$1"

if [ -z "$command" ] ; then 
    exit 1
elif [ "$command" ==  "screen-on" ] ; then
    xset dpms force on	
elif [ "$command" ==  "screen-off" ] ; then
    xset dpms force off
elif [ "$command" ==  "update-repo" ] ; then
    bash ./scripts/sync_repo.sh 
else
    exit 1
fi
