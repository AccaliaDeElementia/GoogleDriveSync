#!/bin/bash

if [ ! \( -d bin -a -d include -a -d lib -a -d local \) ]; then
    echo Creating virtualenv
    virtualenv .
    #virtualenv --relocatable . > /dev/null
    pip install -t ./lib/python-2.7/site-packages google-api-python-client
fi

. bin/activate
