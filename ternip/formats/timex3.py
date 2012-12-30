from ternip.formats.xml_doc import XmlDocument
from ternip.timex import Timex

class Timex3XmlDocument(XmlDocument):
    """
    A class which takes any random XML document and adds TIMEX3 tags to it.
    
    Suitable for use with Timebank, which contains many superfluous tags that
    aren't in the TimeML spec, even though it claims to be TimeML.
    """

    _timex_tag_name = 'TIMEX3'

    def _timex_from_node(self, node):
        """
        Given a node representing a TIMEX3 element, return a timex object
        representing it
        """
        t = Timex()

        if node.hasAttribute('tid'):
            t.id = int(node.getAttribute('tid')[1:])

        if node.hasAttribute('value'):
            t.value = node.getAttribute('value')

        if node.hasAttribute('mod'):
            t.mod = node.getAttribute('mod')

        if node.hasAttribute('type'):
            t.type = node.getAttribute('type')

        if node.hasAttribute('freq'):
            t.freq = node.getAttribute('freq')

        if node.hasAttribute('quant'):
            t.quant = node.getAttribute('quant')

        if node.hasAttribute('comment'):
            t.comment = node.getAttribute('comment')

        if node.getAttribute('temporalFunction'):
            t.temporal_function = True

        if node.hasAttribute('functionInDocument'):
            t.document_role = node.getAttribute('functionInDocument')

        if node.hasAttribute('beginPoint'):
            t.begin_timex = int(node.getAttribute('beginPoint')[1:])

        if node.hasAttribute('endPoint'):
            t.end_timex = int(node.getAttribute('endPoint')[1:])

        if node.hasAttribute('anchorTimeID'):
            t.context = int(node.getAttribute('anchorTimeID')[1:])

        return t

    def _annotate_node_from_timex(self, timex, node):
        """
        Add attributes to this TIMEX3 node
        """

        if timex.id is not None:
            node.setAttribute('tid', 't' + str(timex.id))

        if timex.value is not None:
            node.setAttribute('value', timex.value)

        if timex.mod is not None:
            node.setAttribute('mod', timex.mod)

        if timex.type is not None:
            node.setAttribute('type', timex.type.upper())

        if timex.freq is not None:
            node.setAttribute('freq', timex.freq)

        if timex.comment is not None:
            node.setAttribute('comment', timex.comment)

        if timex.quant is not None:
            node.setAttribute('quant', timex.quant)

        if timex.temporal_function:
            node.setAttribute('temporalFunction', 'true')

        if timex.document_role is not None:
            node.setAttribute('functionInDocument', timex.document_role)

        if timex.begin_timex is not None:
            node.setAttribute('beginPoint', 't' + str(timex.begin_timex.id))

        if timex.end_timex is not None:
            node.setAttribute('endPoint', 't' + str(timex.end_timex.id))

        if timex.context is not None:
            node.setAttribute('anchorTimeID', 't' + str(timex.context.id))
