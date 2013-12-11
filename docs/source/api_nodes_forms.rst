=================
 Nodes and forms
=================

.. contents:: :local:


.. automodule:: ftw.testbrowser.nodes


Result set
==========

.. autoclass:: ftw.testbrowser.nodes.Nodes
   :show-inheritance:
   :members:


Node wrappers
=============

Node wrappers wrap the standard `lxml` elements and extend them with some useful
methods so that it is nicely integrated in the `ftw.testbrowser` behavior.

.. autoclass:: ftw.testbrowser.nodes.NodeWrapper
   :show-inheritance:
   :members:

.. autoclass:: ftw.testbrowser.nodes.LinkNode
   :show-inheritance:
   :members:

.. autoclass:: ftw.testbrowser.nodes.DefinitionListNode
   :show-inheritance:
   :members:



Forms, fields and widgets
=========================

.. automodule:: ftw.testbrowser.form

.. autoclass:: ftw.testbrowser.form.Form
   :show-inheritance:
   :members:

   .. py:classmethod:: find_form_by_labels_or_names
   .. py:classmethod:: find_form_element_by_label_or_name
   .. py:classmethod:: find_field_in_form

.. autoclass:: ftw.testbrowser.form.TextAreaField
   :show-inheritance:
   :members:

.. autoclass:: ftw.testbrowser.form.SubmitButton
   :show-inheritance:
   :members:

.. automodule:: ftw.testbrowser.widgets
   :show-inheritance:
   :members:


Tables
======

.. automodule:: ftw.testbrowser.table
   :show-inheritance:
   :members:
