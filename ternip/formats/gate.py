import copy
from ternip.timex import add_timex_ids


class GateDocument(object):
    """
    A class to facilitate communication with GATE
    """

    def __init__(self, file):
        """
        Load a document
        """

        sents = []
        sent = []
        dct = None

        for line in file.splitlines():
            parts = line.split('\t')
            if dct is None:
                dct = parts[3]
            if parts[2] == 'I':
                sent.append((parts[0], parts[1], set()))
            else:
                if len(sent) > 0:
                    sents.append(sent)
                sent = [(parts[0], parts[1], set())]
        sents.append(sent)

        self._sents = sents
        self._dct = dct

    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        """
        return copy.deepcopy(self._sents)

    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        """
        return [[(self._dct, 'DCT', set())]]

    def reconcile_dct(self, dct):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        pass

    def reconcile(self, sents):
        """
        Update this document with the newly annotated tokens.
        """
        # TIMEXes need unique IDs
        all_ts = set()
        for sent in sents:
            for (tok, pos, ts) in sent:
                for t in ts:
                    all_ts.add(t)
        add_timex_ids(all_ts)
        self._sents = copy.deepcopy(sents)

    def _get_attrs(self, timex):
        attrs = []

        if timex.id is not None:
            attrs.append("id=t" + str(timex.id))

        if timex.value is not None:
            attrs.append("value=" + timex.value)

        if timex.type is not None:
            attrs.append("type=" + timex.type.upper())

        if timex.mod is not None:
            attrs.append("mod=" + timex.mod)

        if timex.freq is not None:
            attrs.append("freq=" + timex.freq)

        if timex.quant is not None:
            attrs.append("quant=" + timex.quant)

        if timex.temporal_function:
            attrs.append("temporalFunction=true")

        if timex.document_role is not None:
            attrs.append("functionInDocument=" + timex.document_role)

        if timex.begin_timex is not None:
            attrs.append("beginPoint=t" + str(timex.begin_timex.id))

        if timex.end_timex is not None:
            attrs.append("endPoint=t" + str(timex.end_timex.id))

        if timex.context is not None:
            attrs.append("anchorTimeID=t" + str(timex.context.id))

        return ','.join(attrs)

    def __str__(self):
        """
        Output format
        """
        s = ''
        open_timexes = set()
        for sent in self._sents:
            for (tok, pos, ts) in sent:
                s += tok + "\t"
                begins = []
                ins = []
                for timex in ts:
                    if timex in open_timexes:
                        ins.append('t' + str(timex.id))
                    else:
                        begins.append(self._get_attrs(timex))
                        open_timexes.add(timex)
                        break
                s += ';'.join(begins) + "\t" + ';'.join(ins) + "\n"
        return s
