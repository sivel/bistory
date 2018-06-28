bistory
=======

A small python application that implements bash history searching in
your terminal

|image0|

Installation
------------

::

    $ pip install --user bistory

Configuration
-------------

.bash_profile
~~~~~~~~~~~~~

::

    if [[ $- =~ .*i.* ]]; then
        bind '"\C-r": "\C-a bistory \C-j"'
    fi

.. |image0| image:: https://raw.githubusercontent.com/sivel/bistory/master/screenshot.png
   :target: https://raw.githubusercontent.com/sivel/bistory/master/screenshot.png
