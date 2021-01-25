Introduction
==================


Drawioedit is a simple interface to edit drawio files. It uses N2G functions and adds some features. 

Features
-----------------

Drawioedit has following features:
    * load embedded drawio from png files
    * set styles of shapes and links
    * all of the N2G drawio features

Installation
------------

Install drawioedit by running:

.. code-block:: bash

    pip3 install drawioedit


Examples
---------

Set the fillcolor of a shape or a link
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import sys
    sys.path.insert(0, "../")
    from drawioedit import DrawIOEdit
    import os
    red='#ff0000'
    base_path=os.path.dirname(os.path.realpath(__file__))
    drawing=DrawIOEdit(file_path=f'{base_path}/input.drawio.svg')
    drawing.set_shape_color('DC1-SW1',red)
    drawing.set_shape_color('bbnew-1',red)
    drawing.set_shape_color('iperf-1',red)
    drawing.set_shape_color('iperf-3',red)

    for link in drawing.find_link_between_nodes('DC1-SW1','bbnew-1'):
        link.attrib['style']=drawing._edit_style(link.attrib['style'],'strokeColor',red)

    for link in drawing.find_link_between_nodes('Backbone-1','BB-new'):
        link.attrib['style']=drawing._edit_style(link.attrib['style'],'strokeColor',red)

    print(f'saving {base_path}/output.drawio.png')
    drawing.save(f'{base_path}/output.drawio.png')
    print(f'saving {base_path}/output.drawio.svg')
    drawing.save(f'{base_path}/output.drawio.svg')
    print(f'saving {base_path}/output.drawio')
    drawing.save(f'{base_path}/output.drawio')


Contribute
----------

- Issue Tracker: https://github.com/jinjamator/drawioedit/issues
- Source Code: https://github.com/jinjamator/drawioedit

Roadmap
-----------------

Selected Roadmap items:
    * add class documentation

For documentation please refer to https://drawioedit.readthedocs.io/en/latest/

License
-----------------

This project is licensed under the Apache License Version 2.0