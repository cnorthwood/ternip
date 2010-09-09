#!/usr/bin/env python

import ternip

# Conditionally import NLTK - can speed up loading if we know we're not going
# to need it
try:
    no_NLTK
except NameError:
    import nltk.tag
    import nltk.tokenize

import xml.dom.minidom
from collections import defaultdict
import sys

class xml_doc:
    """
    An abstract base class which all XML types can inherit from. This implements
    almost everything, apart from the conversion of timex objects to and from
    timex tags in the XML. This is done by child classes 
    """
    
    @staticmethod
    def _add_words_to_node_from_sents(doc, node, sents, tok_offsets=None):
        """
        Uses the given node and adds an XML form of sents to it. The node
        passed in should have no children (be an empty element)
        """
        
        # Just add text here, then leave it up to reconcile to add all other
        # tags
        
        s_offset = 0
        
        for i in range(len(sents)):
            
            for j in range(len(sents[i])):
                (tok, pos, ts) = sents[i][j]
                
                # Do we know what token offsets are in order to reinstate them?
                if tok_offsets != None:
                    # Add whitespace between tokens if needed
                    while s_offset < tok_offsets[i][j]:
                        node.appendChild(doc.createTextNode(' '))
                        s_offset += 1
                
                # Add the text
                node.appendChild(doc.createTextNode(tok))
                
                # If we're not using token offsets, assume a single space is
                # what's used, except if this is the last element.
                if tok_offsets is None:
                    if not (i == len(sents) - 1 and j == len(sents[i]) - 1):
                        node.appendChild(doc.createTextNode(' '))
                else:
                    # Increase our current sentence offset
                    s_offset += len(tok)
        
        node.normalize()
        return node
    
    @staticmethod
    def create(sents, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        """
        This is an abstract function for building XML documents from the
        internal representation only. You are not guaranteed to get out of
        get_sents what you put in here. Sentences and words will be retokenised
        and retagged unless you explicitly add S and LEX tags and the POS
        attribute to the document using the optional arguments.
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        
        tok_offsets is used to correctly reinsert whitespace lost in
        tokenisation. It's in the format of a list of lists of integers, where
        each integer is the offset from the start of the sentence of that token.
        If set to None (the default), then a single space is assumed between
        all tokens.
        
        If add_S is set to something other than false, then the tags to indicate
        sentence boundaries are added, with the name of the tag being the value
        of add_S
        
        add_LEX is similar, but for token boundaries
        
        pos_attr is similar but refers to the name of the attribute on the LEX
        (or whatever) tag that holds the POS tag.
        """
        raise NotImplementedError
    
    def __init__(self, file, nodename=None, has_S=False, has_LEX=False, pos_attr=False):
        """
        Passes in an XML document (as one consecutive string) which is used
        as the basis for this object.
        
        Alternatively, you can pass in an xml.dom.Document class which means
        that it's not parsed. This is used by the static create function.
        
        Node name is the name of the "body" of this document to be considered.
        If set to None (it's default), then the root node is considered to be
        the document body.
        
        has_S means that the document uses XML tags to mark sentence boundaries.
        This defaults to False, but if your XML document does, you should set it
        to the name of your sentence boundary tag (normally 'S').
        
        has_LEX is similar to has_S, but for token boundaries. Again, set this
        to your tag for token boundaries (not as common, but sometimes it's
        'lex')
        
        pos_attr is the name of the attribute on your LEX (or whatever) tags
        that indicates the POS tag for that token.
        
        The tagger needs tokenised sentences and tokenised and POS tagged tokens
        in order to be able to tag. If the input does not supply this data, the
        NLTK is used to fill the blanks. If this input is supplied, it is
        blindly accepted as reasonably sensible. If there are tokens which are
        not annotated (for whatever reason), then alignment between XML nodes
        and the results of the tagging may fail and give undesirable results.
        Similarly, if tokens are embedded inside other tokens, this will also
        error in likely undesirable way, and such a tagging is likely erroneous.
        """
        
        if isinstance(file, xml.dom.minidom.Document):
            self._xml_doc = file
        else:
            self._xml_doc = xml.dom.minidom.parseString(file)
        
        if nodename is None:
            self._xml_body = self._xml_doc.documentElement
        else:
            tags = self._xml_doc.getElementsByTagName(nodename)
            if len(tags) != 1:
                raise bad_node_name_error()
            self._xml_body = tags[0]
        
        self._has_S = has_S
        self._has_LEX = has_LEX
        self._pos_attr = pos_attr
    
    def _strip_tags(self, doc, tagname, node):
        """
        Recursively remove a tag from this node
        """
        
        # Recursive step - depth-first search
        for child in node.childNodes:
            
            # Get the list of nodes which replace this one (if any)
            rep = self._strip_tags(doc, tagname, child)
            
            if len(rep) == 1:
                # If it's a single node that's taking the place of this one (e.g.,
                # if there was no change, or a timex tag that only had some text
                # inside it), but only if the node's changed
                if rep[0] is not child:
                    node.replaceChild(rep[0], child)
            else:
                # There were multiple child nodes, need to insert all of them
                # where in the same location, in order, where their parent
                # node was. Unfortunately replaceChild can't do replacement
                # of a node with multiple nodes.
                before = child.nextSibling
                node.removeChild(child)
                for new_node in rep:
                    node.insertBefore(new_node, before)
                node.normalize()
        
        # Base step
        if node.nodeType == node.ELEMENT_NODE and node.tagName == tagname:
            return [child for child in node.childNodes]
        else:
            return [node]
    
    def strip_tag(self, tagname):
        """
        Remove this tag from the document.
        """
        self._strip_tags(self._xml_doc, tagname, self._xml_body)
    
    def strip_timexes(self):
        """
        Strips all timexes from this document. Useful if we're evaluating the
        software - we can just feed in the gold standard directly and compare
        the output then.
        """
        self._strip_tags(self._xml_doc, self._timex_tag_name, self._xml_body)
    
    def _get_text_recurse(self, element, until = None):
        """
        Given an element, returns only the text only nodes in it concatenated
        together, up until the node specified by until is reached.
        """
        
        cont = True
        text = ""
        
        if element == until:
            # Check if we need to stop
            cont = False
        elif element.nodeType == element.TEXT_NODE:
            # If it's a text node, add the data, and no more recursion
            text += element.data
        else:
            # depth-first search, recursive step
            for child in element.childNodes:
                (cont, t) = self._get_text_recurse(child, until)
                text += t
                if not cont:
                    break
            
        return (cont, text)
    
    def _get_text(self, element, until = None):
        """
        Given an element, returns only the text only nodes in it concatenated
        together, up until the node specified by until is reached.
        """
        return self._get_text_recurse(element, until)[1]
    
    def _can_align_node_sent(self, node, sent):
        """
        Can this sentence be aligned with this node?
        """
        
        text = self._get_text(node)
        texti = 0
        
        # Go through each token and check it can be aligned with somewhere in
        # the text
        for i in range(len(sent)):
            offset = text.find(sent[i][0][0], texti)
            if offset == -1:
                # This token can't be aligned, so we say we can't align, but do
                # say how many tokens were successfully aligned
                return (False, i, texti)
            else:
                texti = offset + len(sent[i][0])
        
        return (True, i, texti)
    
    def _split_text_for_S(self, node, sents, s_name, align_point):
        """
        Given a text node, splits it up into sentences and insert these
        sentences in to an appropriate point in the parent node
        """
        
        # Don't include leading whitespace in the tag
        s_start = node.data.find(sents[0][0][0])
        if s_start > 0:
            node.parentNode.insertBefore(self._xml_doc.createTextNode(node.data[:s_start]), node)
        
        # Create an S tag containing the matched part
        s_tag = self._xml_doc.createElement(s_name)
        s_tag.appendChild(self._xml_doc.createTextNode(node.data[s_start:align_point]))
        
        # Insert this where this match tag is
        node.parentNode.insertBefore(s_tag, node)
        
        # If there's still some text left, then create a new text node with
        # what was left, and then insert that where this text node was, and
        # recurse on it to tag any more sentences, if there are any
        if align_point < len(node.data):
            new_child = self._xml_doc.createTextNode(node.data[align_point:])
            node.parentNode.replaceChild(new_child, node)
            if len(sents) > 1:
                (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(new_child, sents[1])
                if can_align:
                    return self._split_text_for_S(new_child, sents[1:], s_name, text_aligned)
                else:
                    return sents[1:]
            else:
                return []
        else:
            node.parentNode.removeChild(node)
            return sents[1:]
    
    def _handle_adding_S_tag(self, node, sent, sents, s_tag, s_name):
        # If this node contains the entirety of this sentence, and isn't a
        # text node, then recurse on it to break it down
        (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(node, sent)
        if can_align and node.nodeType != node.TEXT_NODE:
            if len(sent) == len(sents[0]):
                # Current sent isn't a partial match, continue as per usual
                sents = self._add_S_tags(node, sents, s_name)
                if len(sents) > 0:
                    sent = list(sents[0])
                else:
                    return (sent, [], s_tag)
            else:
                # Add, because if this is a partial match but found a full
                # node, it contains the rest of the sentence. Or it's a tag
                # which spans sentence boundaries. The latter is bad.
                s_tag.appendChild(node)
        
        elif can_align and node.nodeType == node.TEXT_NODE:
            # If this text node does contain the full sentence so far, then
            # break up that text node and add the text between <s> tags as
            # appropriate
            if len(sent) == len(sents[0]):
                sents = self._split_text_for_S(node, sents, s_name, text_aligned)
                if len(sents) > 0:
                    sent = list(sents[0])
                else:
                    return (sent, [], s_tag)
            else:
                # If we've matched part of a sentence so far, and this
                # text node finishes it off, then break up the text node and
                # add the first bit of it to this node. Then recurse on the
                # rest of it with the remaining sentences
                s_tag.appendChild(self._xml_doc.createTextNode(node.data[:text_aligned]))
                new_child = self._xml_doc.createTextNode(node.data[text_aligned:])
                node.parentNode.replaceChild(new_child, node)
                (can_align, tok_aligned, text_aligned) = self._can_align_node_sent(new_child, sents[1])
                if len(sents) > 1:
                    sent = list(sents[1])
                    sents = sents[1:]
                    if can_align:
                        sents = self._split_text_for_S(new_child, sents, s_name, text_aligned)
                        if len(sents) > 0:
                            sent = list(sents[0])
                        else:
                            return (sent, [], s_tag)
                    else:
                        (sent, sents, s_tag) = self._handle_adding_S_tag(new_child, sent, sents, s_tag, s_name)
            
        else:
            # What we have didn't match the whole sentence, so just add the
            # entire node and then update how little we have left.
            # If this is the first incomplete match we've found (that is,
            # our partial sentence is the same as the full one), then this
            # is a new sentence
            if len(sent) == len(sents[0]):
                s_tag = self._xml_doc.createElement(s_name)
                node.parentNode.insertBefore(s_tag, node)
                if node.nodeType == node.TEXT_NODE:
                    s_start = node.data.find(sent[0][0])
                    if s_start > 0:
                        s_tag.parentNode.insertBefore(self._xml_doc.createTextNode(node.data[:s_start]), s_tag)
                    new_node = self._xml_doc.createTextNode(node.data[s_start:])
                    node.parentNode.replaceChild(new_node, node)
                    node = new_node
            s_tag.appendChild(node)
            
            # update our sentence to a partial match
            sent = sent[tok_aligned:]
            return (sent, sents, s_tag)
        
        return (sent, sents, s_tag)
    
    def _add_S_tags(self, node, sents, s_name):
        """
        Given a node, and some sentences, add tags called s_name such that these
        tags denote sentence boundaries. Return any sentences which could not
        be assigned in this node.
        """
        
        # Base case
        if len(sents) > 0:
            sent = list(sents[0])
        else:
            return []
        
        s_tag = None
        for child in list(node.childNodes):
            (sent, sents, s_tag) = self._handle_adding_S_tag(child, sent, sents, s_tag, s_name)
        
        return sents
    
    def _add_LEX_tags(self, node, sent, LEX_name):
        """
        Given a node and a sentence, enclose the tokens in that sentence with
        tags called LEX_name to mark token boundaries.
        """
        
        if len(sent) > 0:
            # Drill down until we reach a text node, then align tokens so far in
            # that text node.
            if node.nodeType == node.TEXT_NODE:
                tok = sent[0][0]
                text = self._get_text(node)
                start = text.find(tok[0])
                
                # Include any whitespace
                if start == -1:
                    # Could not align in this node, so continue
                    return sent
                elif start > 0:
                    before = self._xml_doc.createTextNode(text[:start])
                    node.parentNode.insertBefore(before, node)
                
                # Now create the LEX tag
                lex_tag = self._xml_doc.createElement(LEX_name)
                lex_tag.appendChild(self._xml_doc.createTextNode(text[start:start+len(tok)]))
                node.parentNode.insertBefore(lex_tag, node)
                
                # Replace the text node with the list tail
                new_text = self._xml_doc.createTextNode(text[start+len(tok):])
                node.parentNode.replaceChild(new_text, node)
                
                # Continue adding for the rest of this LEX node
                sent = sent[1:]
                return self._add_LEX_tags(new_text, sent, LEX_name)
                
            else:
                for child in node.childNodes:
                    sent = self._add_LEX_tags(child, sent, LEX_name)
        
        return sent
    
    def _get_token_extent(self, node, sent):
        if node.nodeType == node.TEXT_NODE:
            i = 0
            texti = 0
            text = node.data
            for (tok, pos, ts) in sent:
                offset = text.find(tok[0], texti)
                if offset < 0:
                    return i
                else:
                    i += 1
                    texti = offset + len(tok)
        else:
            i = 0
            for child in node.childNodes:
                extent = self._get_token_extent(child, sent)
                sent = sent[extent:]
                i += extent
        return i
    
    def _add_timex_child(self, timex, sent, node, start, end):
        i = 0
        timex_tag = None
        for child in list(node.childNodes):
            e = self._get_token_extent(child, sent[i:])
            if (i + e) >= start and i <= start and e > 0:
                if child.nodeType == node.TEXT_NODE:
                    # get length of bit before TIMEX
                    texti = 0
                    for (tok, pos, ts) in sent[i:start]:
                        offset = child.data.find(tok[0], texti)
                        if offset == -1:
                            raise tokenise_error('INTERNAL ERROR: Could not align timex start')
                        texti = offset + len(tok)
                    # Now whitespace before first token
                    texti = child.data.find(sent[start][0][0], texti)
                    if texti == -1:
                        # The start of the TIMEX isn't in this text node
                        texti = len(child.data)
                    
                    timex_tag = self._xml_doc.createElement(self._timex_tag_name)
                    self._annotate_node_from_timex(timex, timex_tag)
                    
                    # Found our split point, so now create two nodes
                    before_text = self._xml_doc.createTextNode(child.data[:texti])
                    new_child = self._xml_doc.createTextNode(child.data[texti:])
                    node.insertBefore(before_text, child)
                    node.insertBefore(timex_tag, child)
                    node.replaceChild(new_child, child)
                    child = new_child
                    i += self._get_token_extent(before_text, sent[i:])
                    e = self._get_token_extent(child, sent[i:])
            
            # This node is completely covered by this TIMEX, so include it
            # inside the TIMEX, unless the timex is non consuming
            if (i + e) <= end and i >= start and not timex.non_consuming and (e > 0 or (i > start and (i + e) < end)) and (child.nodeType != node.TEXT_NODE or (i + e) < end):
                if timex_tag is None:
                    timex_tag = self._xml_doc.createElement(self._timex_tag_name)
                    self._annotate_node_from_timex(timex, timex_tag)
                    node.insertBefore(timex_tag, child)
                timex_tag.appendChild(child)
            
            if ((i + e) > end and i < end and not timex.non_consuming) or \
                ((i + e) == end and i >= start and not timex.non_consuming and e > 0 and child.nodeType == node.TEXT_NODE):
                # This crosses the end boundary, so if our TIMEX consumes text
                # then split the node in half (if it's a text node)
                if child.nodeType == node.TEXT_NODE:
                    texti = 0
                    for (tok, pos, ts) in sent[i:end]:
                        offset = child.data.find(tok[0], texti)
                        if offset == -1:
                            raise tokenise_error('INTERNAL ERROR: Could not align timex end ' + tok + ' ' + child.data)
                        texti = offset + len(tok)
                    
                    # Found our split point, so now create two nodes
                    new_child = self._xml_doc.createTextNode(child.data[texti:])
                    timex_tag.appendChild(self._xml_doc.createTextNode(child.data[:texti]))
                    node.replaceChild(new_child, child)
                    
                else:
                    raise nesting_error('Can not tag TIMEX (' + str(timex) + ') without causing invalid XML nesting')
            
            i += e
    
    def _add_timex(self, timex, sent, s_node):
        # Find start:end indices for this TIMEX
        start = 0
        end = 0
        t_reached = False
        for (tok, pos, ts) in sent:
            if timex not in ts and not t_reached:
                start += 1
                end += 1
            if timex in ts:
                t_reached = True
                end += 1
        
        start_extent = 0
        for child in list(s_node.childNodes):
            extent = self._get_token_extent(child, sent[start_extent:])
            end_extent = start_extent + extent
            if start_extent <= start and end_extent >= end:
                # This child can completely contain the TIMEX, so recurse on it
                # unless it's a text node
                if child.nodeType == child.TEXT_NODE:
                    self._add_timex_child(timex, sent, s_node, start, end)
                    break
                else:
                    self._add_timex(timex, sent[start_extent:end_extent], child)
                    break
            elif start_extent < start and end_extent < end - 1 and end_extent >= start:
                # This child contains the start of the TIMEX, but can't
                # completely hold it, which must mean the parent node is the
                # highest node which contains the TIMEX
                self._add_timex_child(timex, sent, s_node, start, end)
                break
            start_extent = end_extent
    
    def reconcile(self, sents, add_S = False, add_LEX = False, pos_attr=False):
        """
        Reconciles this document against the new internal representation. If
        add_S is set to anything other than False, this means tags are indicated
        to indicate the sentence boundaries, with the tag names being the value
        of add_S. add_LEX is the same, but for marking token boundaries, and
        pos_attr is the name of the attribute which holds the POS tag for that
        token. This is mainly useful for transforming the TERN documents into
        something that GUTime can parse.
        
        If your document already contains S and LEX tags, and add_S/add_LEX is
        set to add them, old S/LEX tags will be stripped first. If pos_attr is
        set and the attribute name differs from the old POS attribute name on
        the lex tag, then the old attribute will be removed.
        
        Sentence/token boundaries will not be altered in the final document
        unless add_S/add_LEX is set. If you have changed the token boundaries in
        the internal representation from the original form, but are not then
        adding them back in, reconciliation may give undefined results.
        
        There are some inputs which would output invalid XML. For example, if
        this document has elements which span multiple sentences, but not whole
        parts of them, then you will be unable to add XML tags and get valid
        XML, so failure will occur in unexpected ways.
        
        If you are adding LEX tags, and your XML document contains tags internal
        to tokens, then reconciliation will fail, as it expects tokens to be in
        a continuous piece of whitespace.
        """
        
        # First, add S tags if need be.
        if add_S:
            
            # First, strip any old ones
            if self._has_S:
                self._strip_tags(self._xml_doc, self._has_S, self._xml_body)
            
            # Then add the new ones
            leftover = self._add_S_tags(self._xml_body, sents, add_S)
            if len(leftover) > 1:
                raise nesting_error('Unable to add all S tags, possibly due to bad tag nesting' + str(leftover))
            
            # Update what we consider to be our S tags
            self._has_S = add_S
        
        # Now, get a list of the S nodes, which are used to reconcile individual
        # tokens
        if self._has_S:
            s_nodes = self._xml_body.getElementsByTagName(self._has_S)
        else:
            # There are no S tokens in the text. So, going forward, only
            # consider there being one sentence, which belongs to the root node
            s_nodes = [self._xml_body]
            new_sent = []
            for sent in sents:
                for part in sent:
                    new_sent.append(part)
            sents = [new_sent]
        
        # Now, add LEX tags if need be
        if add_LEX:
            
            # First, strip any old ones
            if self._has_LEX:
                self._strip_tags(self._xml_doc, self._has_LEX, self._xml_body)
            
            # Now add those LEX tokens
            for i in range(len(sents)):
                self._add_LEX_tags(s_nodes[i], sents[i], add_LEX)
            
            # Update what we consider to be our LEX tags
            self._has_LEX = add_LEX
        
        # Now, add the POS attribute
        if pos_attr and self._has_LEX:
            
            # Get each LEX tag and add the attribute
            for i in range(len(sents)):
                lex_tags = s_nodes[i].getElementsByTagName(self._has_LEX)
                for j in range(len(sents[i])):
                    # Strip the existing attribute if need be
                    try:
                        lex_tags[j].removeAttribute(self._pos_attr)
                    except xml.dom.NotFoundErr:
                        pass
                    
                    # Now set the new POS attr
                    lex_tags[j].setAttribute(pos_attr, sents[i][j][1])
            
            # Update what we think is the pos attr
            self._pos_attr = pos_attr
        
        # Strip old TIMEXes to avoid duplicates
        self.strip_timexes()
        
        # For XML documents, TIMEXes need unique IDs
        all_ts = set()
        for sent in sents:
            for (tok, pos, ts) in sent:
                for t in ts:
                    all_ts.add(t)
        ternip.add_timex_ids(all_ts)
        
        # Now iterate over each sentence
        for i in range(len(sents)):
            
            # Get all timexes in this sentence
            timexes = set()
            for (word, pos, ts) in sents[i]:
                for t in ts:
                    timexes.add(t)
            
            # Now, for each timex, add it to the sentence
            for timex in timexes:
                try:
                    self._add_timex(timex, sents[i], s_nodes[i])
                except nesting_error as e:
                    ternip.warn("Error whilst attempting to add TIMEX", e)
    
    def _nodes_to_sents(self, node, done_sents, nondone_sents, senti):
        """
        Given a node (which spans multiple sentences), a list of sentences which
        have nodes assigned, and those which don't currently have nodes assigned
        """
        
        # Get next not done sent
        (sent, snodes) = nondone_sents[0]
        
        # Align start of node with where we care about
        text = self._get_text(node)
        text = text[text.find(sent[senti]):]
        
        if len(text) > len(sent) - senti and node.nodeType != node.TEXT_NODE:
            # This node is longer than what's remaining in our sentence, so
            # try and find a small enough piece.
            for child in node.childNodes:
                (done_sents, nondone_sents, senti) = self._nodes_to_sents(child, done_sents, nondone_sents, senti)
        
        elif len(text) > len(sent) - senti and node.nodeType == node.TEXT_NODE:
            # It's a text node! Append the relevant part of this text node to
            # this sent
            snodes.append(self._xml_doc.createTextNode(text[:len(sent) - senti]))
            
            # Mark this sentence as done, yay!
            done_sents.append(nondone_sents[0])
            nondone_sents = nondone_sents[1:]
            
            # Now recurse on the next text node
            (done_sents, nondone_sents, senti) = self._nodes_to_sents(self._xml_doc.createTextNode(text[len(sent) - senti:]), done_sents, nondone_sents, 0)
        
        else:
            # This node is shorter or the same length as what's left in this
            # sentence! So we can just add this node
            snodes.append(node)
            nondone_sents[0] = (sent, snodes)
            senti += len(text)
            
            # Now, if that sentence is complete, then move it from nondone into
            # done
            if senti == len(sent):
                done_sents.append(nondone_sents[0])
                nondone_sents = nondone_sents[1:]
                senti = 0
        
        return (done_sents, nondone_sents, senti)
    
    def _timex_node_token_align(self, text, sent, tokeni):
        """
        Given a tokenised sentence and some text, with some starting token
        offset, figure out which is the token after the last token in this
        block of text
        """
        texti = 0
        for (token, pos, timexes) in sent[tokeni:]:
            text_offset = text[texti:].find(sent[tokeni][0][0])
            if text_offset == -1:
                # can't align with what's left, so next token must be a boundary
                break
            else:
                # Move our text point along to the end of the current token,
                # and continue
                texti += text_offset + len(token)
                tokeni += 1
        
        return tokeni
    
    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        
        If there are any TIMEXes in the input document that cross sentence
        boundaries (and the input is not already broken up into sentences with
        the S tag), then those TIMEXes are disregarded.
        """
        
        # Collect all TIMEXs so we can later find those outside of a sentence
        all_timex_nodes = set()
        all_timexes_by_id = dict()
        all_timexes = []
        
        # Is this pre-tokenised into sentences?
        if self._has_S:
            # easy
            sents = [(self._get_text(sent), sent) for sent in self._xml_body.getElementsByTagName(self._has_S)]
        else:
            # Get the text, sentence tokenise it and then assign the content
            # nodes of a sentence to that sentence. This is used for identifying
            # LEX tags, if any, and TIMEX tags, if any, later.
            (nodesents, ndsents, i) = self._nodes_to_sents(self._xml_body, [], [(sent, []) for sent in nltk.tokenize.sent_tokenize(self._get_text(self._xml_body))], 0)
            if len(ndsents) > 0:
                raise tokenise_error('INTERNAL ERROR: there appears to be sentences not assigned to nodes')
            
            # Combine contents under a 'virtual' S tag
            sents = []
            for (sent, nodes) in nodesents:
                s_node = self._xml_doc.createElement('s')
                sents.append((sent, s_node))
                for node in nodes:
                    # Mark any TIMEX nodes as found before the deep copy
                    if node.nodeType == node.ELEMENT_NODE or node.nodeType == node.DOCUMENT_NODE:
                        for timex_tag in node.getElementsByTagName(self._timex_tag_name):
                            all_timex_nodes.add(timex_tag)
                    if node.nodeType == node.ELEMENT_NODE:
                        if node.tagName == self._timex_tag_name:
                            all_timex_nodes.add(node)
                    
                    # Clone the node to avoid destroying our original document
                    # and add it to our virtual S node
                    s_node.appendChild(node.cloneNode(True))
            
        
        # Is this pre-tokenised into tokens?
        if self._has_LEX:
            # Go through each node, and find the LEX tags in there
            tsents = []
            for (sent, s_node) in sents:
                toks = []
                for node in s_node.childNodes:
                    if node.nodeType == node.ELEMENT_NODE and node.tagName == self._has_LEX:
                        # If this is a LEX tag
                        toks.append((self._get_text(node), node))
                    elif node.nodeType == node.ELEMENT_NODE or node.nodeType == node.DOCUMENT_NODE:
                        # get any lex tags which are children of this node
                        # and add them
                        for lex in node.getElementsByTagName(self._has_LEX):
                            toks.append((self._get_text(lex), lex))
                tsents.append((toks, s_node))
        else:
            # Don't need to keep nodes this time, so this is easier than
            # sentence tokenisation
            tsents = [([(tok, None) for tok in nltk.tokenize.word_tokenize(sent)], nodes) for (sent, nodes) in sents]
        
        # Right, now POS tag. If POS is an attribute on the LEX tag, then just
        # use that
        if self._has_LEX and self._pos_attr:
            psents = [([(tok, tag.getAttribute(self._pos_attr)) for (tok, tag) in sent], nodes) for (sent, nodes) in tsents]
        else:
            # use the NLTK
            psents = [([t for t in nltk.tag.pos_tag([s for (s, a) in sent])], nodes) for (sent, nodes) in tsents]
        
        # Now do timexes - first get all timex tags in a sent
        txsents = []
        for (sent, s_node) in psents:
            txsent = [(t, pos, set()) for (t, pos) in sent]
            
            # Get all timexes in this sentence
            timex_nodes = s_node.getElementsByTagName(self._timex_tag_name)
            
            # Now, for each timex tag, create a timex object to
            # represent it
            for timex_node in timex_nodes:
                all_timex_nodes.add(timex_node)
                timex = self._timex_from_node(timex_node)
                
                # Record a reference to it for resolution of attributes which
                # refer to other references later
                all_timexes_by_id[timex.id] = timex
                all_timexes.append(timex)
                
                # Now figure out the extent of it
                timex_body = self._get_text(timex_node)
                timex_before = self._get_text(s_node, timex_node)
                
                # Go through each part of the before text and find the
                # first token in the body of the timex
                tokeni = self._timex_node_token_align(timex_before, txsent, 0)
                
                # Now we have the start token, find the end token from
                # the body of the timex
                tokenj = self._timex_node_token_align(timex_body, txsent, tokeni)
                
                # Handle non-consuming TIMEXes
                if tokeni == tokenj:
                    timex.non_consuming = True
                    txsent[tokeni][2].add(timex)
                else:
                    # Okay, now add this timex to the relevant tokens
                    for (tok, pos, timexes) in txsent[tokeni:tokenj]:
                        timexes.add(timex)
            
            txsents.append(txsent)
        
        # Now get all TIMEX tags which are not inside <s> tags (and assume
        # they're non-consuming)
        for timex_node in self._xml_body.getElementsByTagName(self._timex_tag_name):
            if timex_node not in all_timex_nodes:
                
                # Found a TIMEX that has not been seen before
                all_timex_nodes.add(timex_node)
                timex = self._timex_from_node(timex_node)
                all_timexes_by_id[timex.id] = timex
                all_timexes.append(timex)
                
                # Assume it's non-consuming
                timex.non_consuming = True
                
                # And just add it at the front
                txsents[0][0][2].add(timex)
        
        # Now resolve any dangling references
        for timex in all_timexes:
            if timex.begin_timex != None:
                timex.begin_timex = all_timexes_by_id[timex.begin_timex]
            if timex.end_timex != None:
                timex.end_timex = all_timexes_by_id[timex.end_timex]
            if timex.context != None:
                timex.context = all_timexes_by_id[timex.context]
        
        return txsents
    
    def __str__(self):
        """
        String representation of this document
        """
        return self._xml_doc.toxml()
    
    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        """
        return []
    
    def reconcile_dct(self, dct, add_S = False, add_LEX = False, pos_attr=False):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        pass

class tokenise_error(Exception):
    
    def __init__(self, s):
        self._s = s
    
    def __str__(self):
        return str(self._s)

class nesting_error(Exception):
    
    def __init__(self, s):
        self._s = s
    
    def __str__(self):
        return str(self._s)

class bad_node_name_error(Exception):
        
    def __str__(self):
        return "The specified tag name does not exist exactly once in the document"