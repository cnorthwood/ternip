#!/usr/bin/env python

from collections import defaultdict
import copy

import nltk.tag

from ternip.timex import add_timex_ids


class TempEval2Document(object):
    """
    A class which uses the format of stand-off format of TempEval-2
    """

    @staticmethod
    def create(sents, docid=''):
        """
        Creates a TempEval-2 document from the internal representation
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        """

        # Create a blank document
        d = TempEval2Document('', docid)

        # Add sents
        d.reconcile(sents)

        return d

    @staticmethod
    def load_multi(file, dct_file):
        """
        Load multiple documents from a single base-segmentation.tab
        """

        ds = defaultdict(list)
        dcts = defaultdict(str)

        for line in dct_file.splitlines():
            parts = line.split('\t')
            dcts[parts[0]] = parts[1]

        for line in file.splitlines():
            parts = line.split('\t')
            ds[parts[0]].append(line)

        docs = []

        for d in ds:
            docs.append(TempEval2Document('\n'.join(ds[d]), d, dcts[d]))

        return docs

    def __init__(self, file, docid='', dct='XXXXXXXX'):
        """
        Load a document
        """

        tok_sents = []
        self.docid = docid

        for line in file.splitlines():
            parts = line.split('\t')
            if len(parts) > 3:
                i = int(parts[1])
                j = int(parts[2])

                if len(tok_sents) <= i:
                    tok_sents.insert(i, [])

                tok_sents[i].insert(j, parts[3])

        self._sents = [[(tok, pos, set()) for (tok, pos) in nltk.tag.pos_tag(tok_sent)] for tok_sent in tok_sents]
        self.dct = dct

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
        return [[(self.dct, 'DCT', set())]]

    def reconcile_dct(self, dct):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        pass

    def reconcile(self, sents):
        """
        Update this document with the newly annotated tokens.
        """
        self._sents = copy.deepcopy(sents)

    def _get_timex_line(self, i, j, timex):
        return self.docid + "\t" + str(i) + "\t" + str(j) + "\ttimex3\tt" + str(timex.id) + "\t1"

    def get_extents(self):
        """
        Print out the format suitable for timex-extents.tab
        """

        # TIMEXes need unique IDs
        all_ts = set()
        for sent in self._sents:
            for (tok, pos, ts) in sent:
                for t in ts:
                    all_ts.add(t)
        add_timex_ids(all_ts)

        s = ""
        for i in range(len(self._sents)):
            for j in range(len(self._sents[i])):
                for timex in self._sents[i][j][2]:
                    s += self._get_timex_line(i, j, timex) + "\n"

        return s

    def get_attrs(self):
        """
        Print out the format suitable for timex-attributes.tab
        """

        s = ''

        timexes_done = set()

        for i in range(len(self._sents)):
            for j in range(len(self._sents[i])):
                for timex in self._sents[i][j][2]:
                    # Only need to print attributes once
                    if timex in timexes_done:
                        continue
                    else:
                        timexes_done.add(timex)

                    if timex.value is not None:
                        s += self._get_timex_line(i, j, timex) + "\tvalue\t" + timex.value + "\n"

                    if timex.mod is not None:
                        s += self._get_timex_line(i, j, timex) + "\tmod\t" + timex.mod + "\n"

                    if timex.type is not None:
                        s += self._get_timex_line(i, j, timex) + "\ttype\t" + timex.type.upper() + "\n"

                    if timex.freq is not None:
                        s += self._get_timex_line(i, j, timex) + "\tfreq\t" + timex.freq + "\n"

                    if timex.comment is not None:
                        s += self._get_timex_line(i, j, timex) + "\tcomment\t" + timex.comment + "\n"

                    if timex.quant is not None:
                        s += self._get_timex_line(i, j, timex) + "\tquant\t" + timex.quant + "\n"

                    if timex.temporal_function:
                        s += self._get_timex_line(i, j, timex) + "\ttemporalFunction\ttrue\n"

                    if timex.document_role is not None:
                        s += self._get_timex_line(i, j, timex) + "\tfunctionInDocument\t" + timex.document_role + "\n"

                    if timex.begin_timex is not None:
                        s += self._get_timex_line(i, j, timex) + "\tbeginPoint\tt" + str(timex.begin_timex.id) + "\n"

                    if timex.end_timex is not None:
                        s += self._get_timex_line(i, j, timex) + "\tendPoint\tt" + str(timex.end_timex.id) + "\n"

                    if timex.context is not None:
                        s += self._get_timex_line(i, j, timex) + "\tanchorTimeID\tt" + str(timex.context.id) + "\n"

        return s
