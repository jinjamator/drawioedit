Introduction
==================


Drawioedit is a simple interface to edit drawio files. It uses N2G under the hood but simplifies it's usage and add some features. 

Features
-----------------

Drawioedit has following features:
    * load embedded drawio from png files
    * set styles of shapes
    * all of the N2G drawio features

Installation
------------

Install drawioedit by running:

.. code-block:: bash

    pip3 install drawioedit


Examples
---------

Set the fillcolor of a shape
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from drawioedit import DrawIOEdit
    import os

    drawing=DrawIOEdit(file_path=f'/path/to/test.drawio.png')
    drawing.set_shape_style('R1','fillColor','#ff0000')
    drawing.set_shape_style('R2','fillColor','#0000ff')
    drawing.set_shape_style('not existing','fillColor','#0000ff')

    print(drawing.xml())

Contribute
----------

- Issue Tracker: https://github.com/jinjamator/drawioedit/issues
- Source Code: https://github.com/jinjamator/drawioedit

Roadmap
-----------------

Selected Roadmap items:
    * add support for regeneration of png files with the updated data
    * add support for link styles
    * add class documentation

For documentation please refer to https://drawioedit.readthedocs.io/en/latest/

License
-----------------

This project is licensed under the Apache License Version 2.0