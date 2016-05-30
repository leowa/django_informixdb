django\_informixdb
==================

A database driver for Django to connect to an Informix database via
informixdb python module.

**Some limitations**:
- Do not support default values



Configure local environment
---------------------------

The following environment variable should exist: - INFORMIXDIR -
INFORMIXSERVER - INFROMIXSQLHOSTS
django\_informixdb
==================

A database driver for Django to connect to an Informix database via
informixdb python module.

**Some limitations**:
- Do not support default values


Configure local environment
---------------------------

The following environment variable should exist: - INFORMIXDIR -
INFORMIXSERVER - INFROMIXSQLHOSTS

You need to create a sqlhosts file configuring remote/local informix
server connection information like the following:

::

    ifxserver    onsoctcp     xxx.yy.com  1234
    local_ifxserver1    onsoctcp     *  4567

Configure custom.py
-------------------

Django’s custom.py require the following format to connect to a informix
db:

::

    'default': {
        'ENGINE': 'django_informixdb',
        'NAME': 'myproject',
        'SERVER': 'ifxserver',
        'USER' : 'testuser',
        'PASSWORD': 'passw0rd',
    }


Corresponding informixdb python connection:
-------------------------------------------
::

    import informixdb
    conn = informixdb.connect('myproject@ifxserver', 'testuser', 'passw0rd')
    cursor = conn.cursor()
    cursor.execute('select tabname from systables')
    cursor.fetchall()
    cursor.close()
    conn.close()

