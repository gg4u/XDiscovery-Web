#!/bin/bash

regexp="([a-zA-Z0-9_\-]+)=(.*)"

while IFS=$'\n' read -r line || [[ -n "$line" ]]; do
    n=$(($n+1))
    if [[ $line =~ $regexp ]]; then
	export ${BASH_REMATCH[1]}="${BASH_REMATCH[2]}"
    elif [ "$line" ]; then
	echo "bogus line $n in $1"
    fi
done < "$1"

shift

exec "$@"