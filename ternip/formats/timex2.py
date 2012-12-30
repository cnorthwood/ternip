#!/usr/bin/env python
from ternip.formats.xml_doc import XmlDocument
from ternip.timex import Timex


class Timex2XmlDocument(XmlDocument):
    """
    A class which takes any random XML document and adds TIMEX2 tags to it.
    """

    _timex_tag_name = 'TIMEX2'

    def _timex_from_node(self, node):
        """
        Given a TIMEX2 node, create a timex object with the values of that node
        """
        t = Timex()

        if node.hasAttribute('SET'):
            if node.getAttribute('SET').lower() == 'yes':
                t.type = 'set'
                if node.hasAttribute('PERIODICITY'):
                    t.value = 'P' + node.getAttribute('PERIODICITY')[1:]

        if node.hasAttribute('VAL'):
            t.value = node.getAttribute('VAL')

        if node.hasAttribute('MOD'):
            t.mod = node.getAttribute('MOD')

        if node.hasAttribute('GRANUALITY'):
            t.freq = node.getAttribute('GRANUALITY')[1:]

        if node.hasAttribute('COMMENT'):
            t.comment = node.getAttribute('COMMENT')

        return t

    def _annotate_node_from_timex(self, timex, node):
        """
        Add attributes to this TIMEX2 node
        """

        if timex.value is not None and not (
          len(timex.value) > 0 and timex.value[0] == 'P' and timex.type is not None and timex.type.lower() == 'set'):
            node.setAttribute('VAL', timex.value)

        if timex.mod is not None:
            node.setAttribute('MOD', timex.mod)

        if timex.type is not None and timex.type.lower() == 'set':
            node.setAttribute('SET', 'YES')
            if timex.value is not None and timex.value[0] == 'P':
                node.setAttribute('PERIODICITY', 'F' + timex.value[1:])

        if timex.freq is not None:
            node.setAttribute('GRANUALITY', 'G' + timex.freq)

        if timex.comment is not None:
            node.setAttribute('COMMENT', timex.comment)
