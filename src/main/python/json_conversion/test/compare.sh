#!/usr/bin/env bash

if cmp --silent "$1" "$2"; then
    echo "Success: Compared files are equal"
else
    echo "Error: Compared files are different"
    exit 1
fi
