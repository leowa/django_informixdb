# django_informixdb
A database driver for Django to connect to an Informix database via informixdb python module

## Configure local environment
The following environment variable should exist:
- INFORMIXDIR
- INFORMIXSERVER
- INFROMIXSQLHOSTS

You need to create a sqlhosts file configuring remote/local informix server connection information like the following:
```
ifxserver    onsoctcp     xxx.yy.com  1234
local_ifxserver1    onsoctcp     *  4567
```

## Configure custom.py
Django's custom.py require the following format to connect to a informix db:
```
    'connection': {
       'default': 'django_informixdb',
       'server':<informixserver>,
       'USER': '<username>',
       'PASSWORD': '<password>',
    },
```
