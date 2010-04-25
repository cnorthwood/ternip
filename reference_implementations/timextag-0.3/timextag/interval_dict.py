#!/usr/bin/env python

import sys
import unittest
from sets import Set as set
import UserDict

class IntervalNode(object):
    '''Interval tree (a la CLR) but extended from a simple binary
    search tree rather than a red-black tree'''
    def __init__(self, lower, upper, data):
	self.left = None
	self.right = None
        self.lower = lower
        self.upper = upper
        self.maxima = dict(left=None, right=None)
        self.data = data

    def _str(self, indent=''):
        if self.left and self.right:
	    return 'IntervalNode: [%s, %s], %s (maxes: %s, %s)\n\t%sleft: %s\n\t%sright: %s' % \
                (self.lower, self.upper, self.data, self.maxima['left'], self.maxima['right'],
                 indent, self.left._str('%s\t' % indent),
                 indent, self.right._str('%s\t' % indent))
        elif self.left:
	    return 'IntervalNode: [%s, %s], %s (maxes: %s, %s)\n\t%sleft: %s\n\t%sright: None' % \
                (self.lower, self.upper, self.data, self.maxima['left'], self.maxima['right'],
                 indent, self.left._str('%s\t' % indent), indent)
        elif self.right:
	    return 'IntervalNode: [%s, %s], %s (maxes: %s, %s)\n\t%sleft: None\n\t%sright: %s' % \
                (self.lower, self.upper, self.data, self.maxima['left'], self.maxima['right'],
                 indent, indent, self.right._str('%s\t' % indent))
        else:
	    return 'IntervalNode: [%s, %s], %s (maxes: %s, %s)\n\t%sleft: None\n\t%sright: None' % \
                (self.lower, self.upper, self.data, self.maxima['left'], self.maxima['right'], indent, indent)

    def __repr__(self):
        return self._str()

    def __str__(self):
	if self.left and self.right:
	    return '<IntervalNode: [%s, %s]: %s (l, r)>' % \
		(self.lower, self.upper, self.data)
	elif self.left:
	    return '<IntervalNode: [%s, %s]: %s (l)>' % \
		(self.lower, self.upper, self.data)
	elif self.right:
	    return '<IntervalNode: [%s, %s]: %s (r)>' % \
		(self.lower, self.upper, self.data)
	else:
	    return '<IntervalNode: [%s, %s]: %s>' % \
		(self.lower, self.upper, self.data)

    def __iter__(self):
	if isinstance(self.left, IntervalNode):
	    for node in self.left:
		yield node
	#
	yield self
	#
	if isinstance(self.right, IntervalNode):
	    for node in self.right:
		yield node

    def __eq__(self, other):
	if not isinstance(other, IntervalNode):
	    return False
	return self.lower == other.lower and \
	    self.upper == other.upper and \
	    self.data == other.data and \
	    self.left == other.left and \
	    self.right == other.right and \
	    self.maxima['left'] == other.maxima['left'] and \
	    self.maxima['right'] == other.maxima['right']

    def getlower(self):
	return self.lower

    def getupper(self):
	return self.upper

    def getdata(self):
	return self.data

    def insert(self, lower, upper, data):
	if lower > upper:
	    raise ValueError
        if lower == self.lower and upper == self.upper:
            # Slient replacement
            self.data = data
	elif lower <= self.lower:
	    if self.left:
		self.left.insert(lower, upper, data)
	    else:
		self.left = IntervalNode(lower, upper, data)
	    if self.maxima['left'] is None or upper > self.maxima['left']:
		self.maxima['left'] = upper
	else:
	    if self.right:
		self.right.insert(lower, upper, data)
	    else:
		self.right = IntervalNode(lower, upper, data)
	    if self.maxima['right'] is None or upper > self.maxima['right']:
		self.maxima['right'] = upper

    def delete(self, lower, upper):
        # Changes tree and returns changed tree (or None, if necessary)
        if lower > upper:
            raise ValueError
        if lower < self.lower:
            if self.left is None:
                raise KeyError
            self.left = self.left.delete(lower, upper)
            if self.left:
                self.maxima['left'] = max(self.left.upper,
                                          self.left.maxima['left'],
                                          self.left.maxima['right'])
            else:
                self.maxima['left'] = None
            return self
        elif lower > self.lower:
            if self.right is None:
                raise KeyError
            self.right = self.right.delete(lower, upper)
            if self.right:
                self.maxima['right'] = max(self.right.upper,
                                           self.right.maxima['left'],
                                           self.right.maxima['right'])
            else:
                self.maxima['right'] = None
            return self
        elif upper != self.upper:
            if self.left is None:
                raise KeyError
            self.left = self.left.delete(lower, upper)
            if self.left:
                self.maxima['left'] = max(self.left.upper,
                                          self.left.maxima['left'],
                                          self.left.maxima['right'])
            else:
                self.maxima['left'] = None
            return self
        else:
            if self.left is None and self.right is None:
                return None
            elif self.left is None:
                return self.right
            elif self.right is None:
                return self.left
            else:
                new_self, new_left = self.left.deletemax()
                new_self.right = self.right
                new_self.maxima['right'] = self.maxima['right']
                new_self.left = new_left
                if new_left:
                    new_self.maxima['left'] = max(new_left.upper,
                                                  new_left.maxima['left'],
                                                  new_left.maxima['right'])
                else:
                    new_self.maxima['left'] = None
                return new_self

    def deletemax(self):
        '''Returns a pair of:
           - max_node: the smallest node in the tree rooted at self
           - the root of the tree resulting from deleting max_node'''
        if self.right is None:
            new_self = self.left
            self.left = None
            self.maxima['left'] = None
            return self, new_self
        else:
            max_node, new_right = self.right.deletemax()
            self.right = new_right
            if new_right:
                self.maxima['right'] = max(new_right.upper,
                                           new_right.maxima['left'],
                                           new_right.maxima['right'])
            else:
               self.maxima['right'] = None
            return max_node, self

    def lookup(self, lower, upper):
	if lower > upper:
	    raise ValueError
	if lower == self.lower and upper == self.upper:
	    return self
	elif lower <= self.lower and self.left is not None:
	    return self.left.lookup(lower, upper)
	elif lower > self.lower and self.right is not None:
	    return self.right.lookup(lower, upper)
	else:
	    raise KeyError

    def overlap(self, lower, upper):
	if lower > upper:
	    raise ValueError
	overlaps = []
	if self.lower <= upper and lower <= self.upper:
	    overlaps.append(self)
	if self.left is not None and lower <= self.maxima['left']:
	    overlaps.extend(self.left.overlap(lower, upper))
	if self.right:
	    overlaps.extend(self.right.overlap(lower, upper))
	return overlaps


class TestIntervalNode(unittest.TestCase):
    def setUp(self):
	self.node = IntervalNode(1, 10, 'one-ten')
	self.nodeprime = IntervalNode(1, 10, 'one-ten')
	# Reference for left child insertion
	self.node_leftchild = IntervalNode(1, 10, 'one-ten')
	self.node_leftchild.left = IntervalNode(1, 11, 'one-eleven')
	self.node_leftchild.maxima['left'] = 11
	self.node_leftchildprime = IntervalNode(1, 10, 'one-ten')
	self.node_leftchildprime.left = IntervalNode(1, 11, 'one-eleven')
	self.node_leftchildprime.maxima['left'] = 11
	# Reference for subsequent right child insertion
	self.node_rightchild = IntervalNode(1, 10, 'one-ten')
	self.node_rightchild.left = IntervalNode(1, 11, 'one-eleven')
	self.node_rightchild.right = IntervalNode(6, 6, 'six-six')
	self.node_rightchild.maxima['left'] = 11
	self.node_rightchild.maxima['right'] = 6
	self.node_rightchildprime = IntervalNode(1, 10, 'one-ten')
	self.node_rightchildprime.left = IntervalNode(1, 11, 'one-eleven')
	self.node_rightchildprime.right = IntervalNode(6, 6, 'six-six')
	self.node_rightchildprime.maxima['left'] = 11
	self.node_rightchildprime.maxima['right'] = 6
	# Reference for subsequent left descendant insertion
	self.node_leftdesc = IntervalNode(1, 10, 'one-ten')
	self.node_leftdesc.left = IntervalNode(1, 11, 'one-eleven')
	self.node_leftdesc.right = IntervalNode(6, 6, 'six-six')
	self.node_leftdesc.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_leftdesc.left.maxima['left'] = 15
	self.node_leftdesc.maxima['left'] = 15
	self.node_leftdesc.maxima['right'] = 6
	self.node_leftdescprime = IntervalNode(1, 10, 'one-ten')
	self.node_leftdescprime.left = IntervalNode(1, 11, 'one-eleven')
	self.node_leftdescprime.right = IntervalNode(6, 6, 'six-six')
	self.node_leftdescprime.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_leftdescprime.left.maxima['left'] = 15
	self.node_leftdescprime.maxima['left'] = 15
	self.node_leftdescprime.maxima['right'] = 6
	# Reference for subsequent right descendant insertion
	self.node_rightdesc = IntervalNode(1, 10, 'one-ten')
	self.node_rightdesc.left = IntervalNode(1, 11, 'one-eleven')
	self.node_rightdesc.right = IntervalNode(6, 6, 'six-six')
	self.node_rightdesc.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_rightdesc.left.maxima['left'] = 15
	self.node_rightdesc.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_rightdesc.right.maxima['left'] = 20
	self.node_rightdesc.maxima['left'] = 15
	self.node_rightdesc.maxima['right'] = 20
	self.node_rightdescprime = IntervalNode(1, 10, 'one-ten')
	self.node_rightdescprime.left = IntervalNode(1, 11, 'one-eleven')
	self.node_rightdescprime.right = IntervalNode(6, 6, 'six-six')
	self.node_rightdescprime.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_rightdescprime.left.maxima['left'] = 15
	self.node_rightdescprime.right.left = IntervalNode(3, 20,
							   'three-twenty')
	self.node_rightdescprime.right.maxima['left'] = 20
	self.node_rightdescprime.maxima['left'] = 15
	self.node_rightdescprime.maxima['right'] = 20
	# Reference for three-level tree insertion
	self.node_3level = IntervalNode(2, 10, 'two-ten')
	self.node_3level.left = IntervalNode(1, 11, 'one-eleven')
	self.node_3level.right = IntervalNode(4, 9, 'four-nine')
	self.node_3level.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_3level.left.right = IntervalNode(2, 25, 'two-25')
	self.node_3level.left.maxima['left'] = 15
	self.node_3level.left.maxima['right'] = 25
	self.node_3level.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_3level.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_3level.right.maxima['left'] = 20
	self.node_3level.right.maxima['right'] = 40
	self.node_3level.maxima['left'] = 25
	self.node_3level.maxima['right'] = 40
	self.node_3levelprime = IntervalNode(2, 10, 'two-ten')
	self.node_3levelprime.left = IntervalNode(1, 11, 'one-eleven')
	self.node_3levelprime.right = IntervalNode(4, 9, 'four-nine')
	self.node_3levelprime.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_3levelprime.left.right = IntervalNode(2, 25, 'two-25')
	self.node_3levelprime.left.maxima['left'] = 15
	self.node_3levelprime.left.maxima['right'] = 25
	self.node_3levelprime.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_3levelprime.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_3levelprime.right.maxima['left'] = 20
	self.node_3levelprime.right.maxima['right'] = 40
	self.node_3levelprime.maxima['left'] = 25
	self.node_3levelprime.maxima['right'] = 40
        # Reference for replacement (insertion with identical keys)
	self.node_3leveldiff = IntervalNode(2, 10, 'two-ten')
	self.node_3leveldiff.left = IntervalNode(1, 11, 'one-eleven')
	self.node_3leveldiff.right = IntervalNode(4, 9, '4-9')
	self.node_3leveldiff.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_3leveldiff.left.right = IntervalNode(2, 25, '2-twenty-five')
	self.node_3leveldiff.left.maxima['left'] = 15
	self.node_3leveldiff.left.maxima['right'] = 25
	self.node_3leveldiff.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_3leveldiff.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_3leveldiff.right.maxima['left'] = 20
	self.node_3leveldiff.right.maxima['right'] = 40
	self.node_3leveldiff.maxima['left'] = 25
	self.node_3leveldiff.maxima['right'] = 40
        # Reference for deletion
	self.node_del0 = IntervalNode(2, 10, 'two-ten')
	self.node_del0.left = IntervalNode(1, 11, 'one-eleven')
	self.node_del0.right = IntervalNode(3, 9, 'three-nine')
	self.node_del0.left.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_del0.left.right = IntervalNode(2, 25, 'two-25')
        self.node_del0.left.right.left = IntervalNode(2, 10, 'two-ten')
        self.node_del0.left.right.maxima['left'] = 10
	self.node_del0.left.maxima['left'] = 15
	self.node_del0.left.maxima['right'] = 25
	self.node_del0.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_del0.right.left.left = IntervalNode(3, 10, 'three-ten')
        self.node_del0.right.left.maxima['left'] = 10
	self.node_del0.right.left.left.left = IntervalNode(3, 5, 'three-five')
        self.node_del0.right.left.left.maxima['left'] = 5
	self.node_del0.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_del0.right.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del0.right.right.maxima['right'] = 10
	self.node_del0.right.maxima['left'] = 20
	self.node_del0.right.maxima['right'] = 40
	self.node_del0.maxima['left'] = 25
	self.node_del0.maxima['right'] = 40
        self.node_del1 = IntervalNode(2, 25, 'two-25')
        self.node_del1.left = IntervalNode(1, 11, 'one-eleven')
	self.node_del1.left.left = IntervalNode(0, 15, 'zero-fifteen')
        self.node_del1.left.right = IntervalNode(2, 10, 'two-ten')
	self.node_del1.left.maxima['left'] = 15
	self.node_del1.left.maxima['right'] = 10
	self.node_del1.right = IntervalNode(3, 9, 'three-nine')
	self.node_del1.right.left = IntervalNode(3, 20, 'three-twenty')
	self.node_del1.right.left.left = IntervalNode(3, 10, 'three-ten')
        self.node_del1.right.left.maxima['left'] = 10
	self.node_del1.right.left.left.left = IntervalNode(3, 5, 'three-five')
        self.node_del1.right.left.left.maxima['left'] = 5
	self.node_del1.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_del1.right.maxima['left'] = 20
	self.node_del1.right.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del1.right.right.maxima['right'] = 10
	self.node_del1.right.maxima['right'] = 40
	self.node_del1.maxima['left'] = 15
	self.node_del1.maxima['right'] = 40
        self.node_del2 = IntervalNode(2, 25, 'two-25')
        self.node_del2.left = IntervalNode(1, 11, 'one-eleven')
	self.node_del2.left.left = IntervalNode(0, 15, 'zero-fifteen')
        self.node_del2.left.right = IntervalNode(2, 10, 'two-ten')
	self.node_del2.left.maxima['left'] = 15
	self.node_del2.left.maxima['right'] = 10
	self.node_del2.right = IntervalNode(3, 20, 'three-twenty')
	self.node_del2.right.left = IntervalNode(3, 10, 'three-ten')
        self.node_del2.right.maxima['left'] = 10
	self.node_del2.right.left.left = IntervalNode(3, 5, 'three-five')
        self.node_del2.right.left.maxima['left'] = 5
	self.node_del2.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_del2.right.maxima['right'] = 40
	self.node_del2.right.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del2.right.right.maxima['right'] = 10
	self.node_del2.maxima['left'] = 15
	self.node_del2.maxima['right'] = 40
        self.node_del3 = IntervalNode(2, 25, 'two-25')
        self.node_del3.left = IntervalNode(0, 15, 'zero-fifteen')
        self.node_del3.left.right = IntervalNode(2, 10, 'two-ten')
        self.node_del3.left.maxima['right'] = 10
	self.node_del3.right = IntervalNode(3, 20, 'three-twenty')
	self.node_del3.right.left = IntervalNode(3, 10, 'three-ten')
        self.node_del3.right.maxima['left'] = 10
	self.node_del3.right.left.left = IntervalNode(3, 5, 'three-five')
        self.node_del3.right.left.maxima['left'] = 5
	self.node_del3.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_del3.right.maxima['right'] = 40
	self.node_del3.right.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del3.right.right.maxima['right'] = 10
	self.node_del3.maxima['left'] = 15
	self.node_del3.maxima['right'] = 40
        self.node_del4 = IntervalNode(2, 25, 'two-25')
        self.node_del4.left = IntervalNode(0, 15, 'zero-fifteen')
        self.node_del4.left.right = IntervalNode(2, 10, 'two-ten')
        self.node_del4.left.maxima['right'] = 10
	self.node_del4.right = IntervalNode(3, 20, 'three-twenty')
	self.node_del4.right.left= IntervalNode(3, 5, 'three-five')
        self.node_del4.right.maxima['left'] = 5
	self.node_del4.right.right = IntervalNode(5, 40, 'five-forty')
	self.node_del4.right.maxima['right'] = 40
	self.node_del4.right.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del4.right.right.maxima['right'] = 10
	self.node_del4.maxima['left'] = 15
	self.node_del4.maxima['right'] = 40
        self.node_del5 = IntervalNode(2, 25, 'two-25')
        self.node_del5.left = IntervalNode(0, 15, 'zero-fifteen')
        self.node_del5.left.right = IntervalNode(2, 10, 'two-ten')
        self.node_del5.left.maxima['right'] = 10
	self.node_del5.right = IntervalNode(3, 20, 'three-twenty')
	self.node_del5.right.left= IntervalNode(3, 5, 'three-five')
        self.node_del5.right.maxima['left'] = 5
	self.node_del5.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del5.right.maxima['right'] = 10
	self.node_del5.maxima['left'] = 15
	self.node_del5.maxima['right'] = 20
        self.node_del6 = IntervalNode(2, 10, 'two-ten')
        self.node_del6.left = IntervalNode(0, 15, 'zero-fifteen')
	self.node_del6.right = IntervalNode(3, 20, 'three-twenty')
	self.node_del6.right.left= IntervalNode(3, 5, 'three-five')
        self.node_del6.right.maxima['left'] = 5
	self.node_del6.right.right = IntervalNode(6, 10, 'six-ten')
	self.node_del6.right.maxima['right'] = 10
        self.node_del6.maxima['left'] = 15
	self.node_del6.maxima['right'] = 20
        # Reference for full tree overlap
	self.tree = IntervalNode(2, 5, 'two-five')
	self.tree.insert(1, 6, 'one-six')
	self.tree.insert(2, 4, 'two-four')
	self.tree.insert(0, 3, 'zero-three')
	self.tree.insert(16, 18, 'fifteen-eighteen')
	self.tree.insert(13, 13, 'thirteen-thirteen')
	self.tree.insert(20, 30, 'twenty-thirty')

    def test_equal(self):
	self.assertNotEqual(self.node, 'not an interval')
	self.assertEquals(self.node, self.nodeprime)
	self.assertEquals(self.node_leftchild, self.node_leftchildprime)
	self.assertEquals(self.node_rightchild, self.node_rightchildprime)
	self.assertEquals(self.node_leftdesc, self.node_leftdescprime)
	self.assertEquals(self.node_rightdesc, self.node_rightdescprime)
	self.assertEquals(self.node_3level, self.node_3levelprime)

    def test_str_repr(self):
	print self.node_del0
	print repr(self.node_del0)
	print self.node
	print self.node_leftchild
	print self.node_del0.right.right

    def test_insert(self):
	# Insertion error
	self.assertRaises(ValueError, self.node.insert,
			  10, 9, 'ten-nine')
	# Insert left child
	self.node.insert(1, 11, 'one-eleven')
	self.assertEquals(self.node, self.node_leftchild)
	# Insert right child
	self.node.insert(6, 6, 'six-six')
	self.assertEquals(self.node, self.node_rightchild)
	# Insert left descendant
	self.node.insert(0, 15, 'zero-fifteen')
	self.assertEquals(self.node, self.node_leftdesc)
	# Insert right descendant
	self.node.insert(3, 20, 'three-twenty')
	self.assertEquals(self.node, self.node_rightdesc)
	# Create three-level tree
	tree = IntervalNode(2, 10, 'two-ten')
	tree.insert(1, 11, 'one-eleven')
	tree.insert(2, 25, 'two-25')
	tree.insert(0, 15, 'zero-fifteen')
	tree.insert(4, 9, 'four-nine')
	tree.insert(5, 40, 'five-forty')
	tree.insert(3, 20, 'three-twenty')
	self.assertEquals(tree, self.node_3level)
        # Test replacement
        self.node_3level.insert(2, 25, '2-twenty-five')
        self.node_3level.insert(4, 9, '4-9')
        self.assertEquals(self.node_3level, self.node_3leveldiff)
        self.node_3level.insert(4, 9, 'four-nine')
        self.assertNotEqual(self.node_3level, self.node_3leveldiff)

    def test_delete(self):
        # Test leaf deletion
        delete1 = self.node_rightdescprime.delete(3, 20)
        self.assertNotEqual(delete1, self.node_rightdesc)
        self.assertEqual(delete1, self.node_leftdesc)
        delete2 = delete1.delete(0, 15)
        self.assertNotEqual(delete2, self.node_leftdesc)
        self.assertEqual(delete2, self.node_rightchild)
        delete3 = delete2.delete(6, 6)
        self.assertNotEqual(delete3, self.node_rightchild)
        self.assertEqual(delete3, self.node_leftchild)
        delete4 = delete3.delete(1, 11)
        self.assertNotEqual(delete4, self.node_leftchild)
        self.assertEqual(delete4, self.node)
        delete5 = delete4.delete(1, 10)
        self.assertNotEqual(delete5, self.node)
        self.assert_(delete5 is None)
        # Test intermediate node deletion
        delete1 = self.node_del0.delete(2, 10)
        self.assertEqual(delete1, self.node_del1)
        delete2 = delete1.delete(3, 9)
        self.assertEqual(delete2, self.node_del2)
        delete3 = delete2.delete(1, 11)
        self.assertEqual(delete3, self.node_del3)
        delete4 = delete3.delete(3, 10)
        self.assertEqual(delete4, self.node_del4)
        delete5 = delete4.delete(5, 40)
        self.assertEqual(delete5, self.node_del5)
        delete6 = delete5.delete(2, 25)
        self.assertEqual(delete6, self.node_del6)
        # Test exceptions
        self.assertRaises(KeyError, delete6.delete, -1, 15)
        self.assertRaises(KeyError, delete6.delete, 0, 14)
        self.assertRaises(KeyError, delete6.delete, 3, 14)
        self.assertRaises(KeyError, delete6.delete, 4, 10)
        self.assertRaises(KeyError, delete6.delete, 6, 9)
        self.assertRaises(KeyError, delete6.delete, 8, 15)
        self.assertRaises(ValueError, delete6.delete, 10, 6)

    def test_lookup(self):
	self.assertRaises(KeyError, self.node.lookup, 0, 10)
	self.assertRaises(KeyError, self.node.lookup, 2, 9)
	self.assertRaises(ValueError, self.node.lookup, 10, 1)
	self.assertEquals(self.node.lookup(1, 10), self.node)
	self.assertEquals(self.node_3level.lookup(2, 10), self.node_3level)
	self.assertEquals(self.node_3level.lookup(1, 11), self.node_3level.left)
	self.assertEquals(self.node_3level.lookup(2, 25),
			  self.node_3level.left.right)
	self.assertEquals(self.node_3level.lookup(0, 15),
			  self.node_3level.left.left)
	self.assertEquals(self.node_3level.lookup(4, 9),
			  self.node_3level.right)
	self.assertEquals(self.node_3level.lookup(5, 40),
			  self.node_3level.right.right)
	self.assertEquals(self.node_3level.lookup(3, 20),
			  self.node_3level.right.left)
	self.assertRaises(KeyError, self.node_3level.lookup, 2, 15)
	self.assertRaises(KeyError, self.node_3level.lookup, -1, 0)
	self.assertRaises(KeyError, self.node_3level.lookup, 40, 50)
	self.assertRaises(KeyError, self.node_3level.lookup, 45, 50)
	self.assertRaises(ValueError, self.node_3level.lookup, 11, 1)

    def test_overlap(self):
	self.assertRaises(ValueError, self.node.overlap, 10, 1)
	self.assertRaises(ValueError, self.node_3level.overlap, 55, 50)
	self.assertEquals(self.node.overlap(1, 10), [self.node])
	self.assertEquals(self.node.overlap(-1, 1), [self.node])
	self.assertEquals(self.node.overlap(-1, 5), [self.node])
	self.assertEquals(self.node.overlap(1, 1), [self.node])
	self.assertEquals(self.node.overlap(1, 5), [self.node])
	self.assertEquals(self.node.overlap(5, 9), [self.node])
	self.assertEquals(self.node.overlap(6, 6), [self.node])
	self.assertEquals(self.node.overlap(4, 10), [self.node])
	self.assertEquals(self.node.overlap(10, 10), [self.node])
	self.assertEquals(self.node.overlap(10, 50), [self.node])
	self.assertEquals(self.node.overlap(-1, 0), [])
	self.assertEquals(self.node.overlap(0, 0), [])
	self.assertEquals(self.node.overlap(11, 11), [])
	self.assertEquals(self.node.overlap(11, 15), [])
	self.assertEquals(len(self.node_rightdesc.overlap(5, 7)), 5)
	self.assertEquals(set(self.node_rightdesc.overlap(5, 7)),
			  set([self.node_rightdesc,
			       self.node_rightdesc.left,
			       self.node_rightdesc.left.left,
			       self.node_rightdesc.right,
			       self.node_rightdesc.right.left]))
	self.assertEquals(len(self.node_rightdesc.overlap(7, 8)), 4)
	self.assertEquals(set(self.node_rightdesc.overlap(7, 8)),
			  set([self.node_rightdesc,
			       self.node_rightdesc.left,
			       self.node_rightdesc.left.left,
			       self.node_rightdesc.right.left]))
	self.assertEquals(self.tree.overlap(-10, -1), [])
	self.assertEquals(self.tree.overlap(0, 0), [self.tree.left.left])
	self.assertEquals(len(self.tree.overlap(0, 10)), 4)
	self.assertEquals(set(self.tree.overlap(0, 10)),
			  set([self.tree,
			       self.tree.left,
			       self.tree.left.left,
			       self.tree.left.right]))
	self.assertEquals(len(self.tree.overlap(5, 15)), 3)
	self.assertEquals(set(self.tree.overlap(5, 15)),
			  set([self.tree,
			       self.tree.left,
			       self.tree.right.left]))
	self.assertEquals(len(self.tree.overlap(6, 13)), 2)
	self.assertEquals(set(self.tree.overlap(6, 13)),
			  set([self.tree.left,
			       self.tree.right.left]))
	self.assertEquals(self.tree.overlap(7, 12), [])
	self.assertEquals(self.tree.overlap(7, 13), [self.tree.right.left])
	self.assertEquals(len(self.tree.overlap(7, 19)), 2)
	self.assertEquals(set(self.tree.overlap(7, 19)),
			  set([self.tree.right,
			       self.tree.right.left]))
	self.assertEquals(len(self.tree.overlap(14, 20)), 2)
	self.assertEquals(set(self.tree.overlap(14, 20)),
			  set([self.tree.right,
			       self.tree.right.right]))
	self.assertEquals(self.tree.overlap(19, 21), [self.tree.right.right])
	self.assertEquals(self.tree.overlap(31, 50), [])

    def test_iter(self):
	i = iter(self.node)
	self.assertEquals(list(i), [self.node])
	i = iter(self.node_rightdesc)
	self.assertEquals(list(i), [self.node_rightdesc.left.left,
				    self.node_rightdesc.left,
				    self.node_rightdesc,
				    self.node_rightdesc.right.left,
				    self.node_rightdesc.right])
	i = iter(self.tree)
	self.assertEquals(list(i), [self.tree.left.left,
				    self.tree.left,
				    self.tree.left.right,
				    self.tree,
				    self.tree.right.left,
				    self.tree.right,
				    self.tree.right.right])


class IntervalDict(object):
    '''Interval dictionary: values indexed by (integral) intervals.
    Assignment via tuples or slices:
    d[1, 10] = 'foo'
    d[(17, 25)] = 'bar'
    d[4:14] = 'bee'
    By-tuple retrieval yields values:
    d[1, 10] -> 'foo'
    d[2, 9] -> KeyError
    By-item retrieval yields list of containing values (no order guarantees):
    d[1] = ['foo']
    d[5] = ['foo', bee']
    d[11] = []
    d[20] = ['bar']
    By-slice retrieval yields list of overlapping values (no order guarantees):
    d[1:10] -> ['foo', 'bee']
    d[3:18] -> ['foo', 'bee', 'bar']
    d[26:100] -> []
    ==, del, len(), keys(), values(), items() work as expected.
    in and has_key() test exact match tuples and item containment.
    '''
    def __init__(self, initial_list=None):
	self.root = None
	if initial_list is None: initial_list = []
	for (lower, upper), data in initial_list:
	    self._insert(lower, upper, data)

    def _insert(self, lower, upper, data):
	if self.root is None:
	    self.root = IntervalNode(lower, upper, data)
	else:
	    self.root.insert(lower, upper, data)

    def _overlap(self, lower, upper):
	if self.root is None:
	    return []
	else:
	    return self.root.overlap(lower, upper)

    def __str__(self):
	return '{%s}' % ', '.join([ '%s:%s' % (key, repr(val)) for (key, val)
				    in zip(self.keys(), self.values()) ])

    def __repr__(self):
	return '{%s}' % ', '.join([ '%s:%s' % (key, repr(val)) for (key, val)
				    in zip(self.keys(), self.values()) ])

    def __contains__(self, args):
	if isinstance(args, tuple) or isinstance(args, list):
	    if len(args) == 2:
		try:
		    return self.root is not None and \
			isinstance(self.root.lookup(args[0], args[1]),
				   IntervalNode)
		except KeyError:
		    return False
	    else:
		raise TypeError
	else:
	    return self[args] != []

    def __len__(self):
	if self.root:
	    return len(list(iter(self.root)))
	else:
	    return 0

    def __eq__(self, other):
        return self.items() == other.items()

    def __setitem__(self, (lower, upper), val):
        self._insert(lower, upper, val)

    def __getitem__(self, arg):
        if isinstance(arg, tuple) or isinstance(arg, list):
            if self.root is None:
                raise KeyError
            lower, upper = arg
	    return self.root.lookup(lower, upper).getdata()
        else:
	    return [ node.getdata() for node in self._overlap(arg, arg) ]

    def __delitem__(self, (lower, upper)):
        self.root = self.root.delete(lower, upper)

    def __setslice__(self, lower, upper, data):
	self._insert(lower, upper, data)

    def __getslice__(self, lower, upper):
        try:
	    return [ node.getdata() for node in self._overlap(lower, upper) ]
        except ValueError:
            return []

    def __delslice__(self, lower, upper):
        self.root = self.root.delete(lower, upper)

    def has_key(self, *args):
	if len(args) == 1:
	    return args[0] in self
	elif len(args) == 2:
	    return args in self
	else:
	    raise ValueError

    def keys(self):
	if self.root is None:
	    return []
	return [ (node.getlower(), node.getupper())
		 for node in list(iter(self.root)) ]

    def values(self):
	if self.root is None:
	    return []
	return [ node.getdata() for node in list(iter(self.root)) ]

    def items(self):
	if self.root is None:
	    return []
	return [ ((node.getlower(), node.getupper()), node.getdata())
		 for node in list(iter(self.root)) ]


class IntervalDict(UserDict.DictMixin):
    def __init__(self, initial_list=None):
	self.root = None
	if initial_list is not None:
	    for (lower, upper), data in initial_list:
		self._insert(lower, upper, data)

    def _insert(self, lower, upper, data):
	if self.root is None:
	    self.root = IntervalNode(lower, upper, data)
	else:
	    self.root.insert(lower, upper, data)

    def _overlap(self, lower, upper):
	if self.root is None:
	    return []
	else:
	    return self.root.overlap(lower, upper)

    def __contains__(self, args):
	if not isinstance(args, list) and not isinstance(args, tuple):
	    return self[args] != []
	else:
	    try:
		self[args]
		return True
	    except KeyError:
		return False

    def __getitem__(self, key):
        if isinstance(key, tuple) or isinstance(key, list):
	    if len(key) != 2:
		raise TypeError
            if self.root is None:
                raise KeyError
            lower, upper = key
	    return self.root.lookup(lower, upper).getdata()
	elif isinstance(key, slice):
	    return [ node.getdata() for node
		     in self._overlap(key.start, key.stop) ]
        else:
	    return [ node.getdata() for node in self._overlap(key, key) ]

    def __setitem__(self, key, val):
	if isinstance(key, tuple) or isinstance(key, list):
	    if len(key) != 2:
		raise TypeError
	    lower, upper = key
	    self._insert(lower, upper, val)
	elif isinstance(key, slice):
	    self._insert(key.start, key.stop, val)
	else:
	    raise TypeError
	
    def __delitem__(self, key):
	if isinstance(key, tuple) or isinstance(key, list):
	    if len(key) != 2:
		raise TypeError
	    lower, upper = key
	    self.root = self.root.delete(lower, upper)
	elif isinstance(key, slice):
	    self.root = self.root.delete(key.start, key.stop)
	else:
	    raise TypeError

    def __iter__(self):
	if self.root is None: self.root =  []
	for node in self.root:
	    yield (node.getlower(), node.getupper())

    def has_key(self, *args):
	if len(args) == 1:
	    if not isinstance(args[0], list) and not isinstance(args[0], tuple):
		return self[args[0]] != []
	    else:
		args = args[0]
	try:
	    self[args]
	    return True
	except KeyError:
	    return False

    def keys(self):
	return list(self.__iter__())

class TestIntervalDict(unittest.TestCase):
    def setUp(self):
	self.empty_fixture = IntervalDict()
	self.fixture = IntervalDict()
        self.fixture.root = IntervalNode(4, 7, 'four-seven')
	self.fixture.root.insert(1, 5, 'one-five')
	self.fixture.root.insert(15, 20, 'fifteen-twenty')
	self.fixture.root.insert(2, 4, 'two-four')
	self.fixtureprime = IntervalDict()
        self.fixtureprime.root = IntervalNode(15, 20, 'fifteen-twenty')
	self.fixtureprime.root.insert(2, 4, 'two-four')
	self.fixtureprime.root.insert(4, 7, 'four-seven')
	self.fixtureprime.root.insert(1, 5, 'one-five')
	self.fixturekeydiff = IntervalDict()
        self.fixturekeydiff.root = IntervalNode(4, 7, 'four-seven')
	self.fixturekeydiff.root.insert(0, 5, 'zero-five')
	self.fixturekeydiff.root.insert(15, 20, 'fifteen-twenty')
	self.fixturekeydiff.root.insert(2, 4, 'two-four')
	self.fixturevaldiff = IntervalDict()
        self.fixturevaldiff.root = IntervalNode(4, 7, 'four-seven')
	self.fixturevaldiff.root.insert(1, 5, 'one-five')
	self.fixturevaldiff.root.insert(15, 20, '15-20')
	self.fixturevaldiff.root.insert(2, 4, 'two-four')

    def test_init(self):
	new_dict = IntervalDict([ ((1, 5), 'one-five'),
				  ((2, 4), 'two-four'),
				  ((4, 7), 'four-seven'),
				  ((15, 20), 'fifteen-twenty') ])
	self.assertEqual(new_dict, self.fixture)

    def test_str_repr(self):
	print self.fixture
	print repr(self.fixture)

    def test_equal(self):
	self.assertNotEqual(self.empty_fixture, self.fixture)
	self.assertEqual(self.fixture, self.fixtureprime)
	self.assertNotEqual(self.fixture, self.fixturekeydiff)
	self.assertNotEqual(self.fixture, self.fixturevaldiff)
	self.assertNotEqual(self.fixturekeydiff, self.fixturevaldiff)

    def test_contains(self):
	self.failIf(5 in self.empty_fixture)
	self.failIf((1, 10) in self.empty_fixture)
	self.assertRaises(TypeError, self.empty_fixture.__contains__,
			  (1, 5, 10))
	self.assert_(1 in self.fixture)
	self.assert_(6 in self.fixture)
	self.assert_(18 in self.fixture)
	self.assert_((4, 7) in self.fixture)
	self.assert_((1, 5) in self.fixture)
	self.assert_((15, 20) in self.fixture)
	self.assert_((2, 4) in self.fixture)
	self.failIf((1, 6) in self.fixture)
	self.failIf((16, 19) in self.fixture)
	self.failIf(0 in self.fixture)
	self.failIf(8 in self.fixture)
	self.failIf(26 in self.fixture)
	self.failIf((-5, 0) in self.fixture)
	self.failIf((8, 12) in self.fixture)
	self.failIf((21, 24) in self.fixture)
	self.assertRaises(TypeError, self.fixture.__contains__, (1, 5, 10))

    def test_len(self):
	self.assertEqual(len(self.empty_fixture), 0)
	self.assertEqual(len(self.fixture), 4)

    def test_setitem(self):
        self.empty_fixture[1, 5] = 'one-five'
        self.empty_fixture[2, 4] = 'two-four'
        self.empty_fixture[4, 7] = 'four-seven'
        self.empty_fixture[15, 20] = 'fifteen-twenty'
        self.assertEquals(self.empty_fixture, self.fixture)
	self.assertRaises(TypeError, self.fixture.__setitem__, 5, 'five')

    def test_getitem(self):
        # Test getting pair keys
        self.assertEqual(self.fixture[1, 5], 'one-five')
        self.assertEqual(self.fixture[2, 4], 'two-four')
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertEqual(self.fixture[15, 20], 'fifteen-twenty')
	self.assertRaises(KeyError, self.empty_fixture.__getitem__, (1, 10))
	self.assertRaises(KeyError, self.fixture.__getitem__, (-1, 0))
	self.assertRaises(KeyError, self.fixture.__getitem__, (3, 8))
	self.assertRaises(KeyError, self.fixture.__getitem__, (4, 6))
	self.assertRaises(KeyError, self.fixture.__getitem__, (21, 26))
	self.assertRaises(ValueError, self.fixture.__getitem__, (7, 4))
        # Test finding singleton keys
	self.assertEqual(self.empty_fixture[5], [])
	self.assertEqual(self.fixture[0], [])
	self.assertEqual(self.fixture[1], ['one-five'])
	self.assertEqual(self.fixture[2], ['one-five', 'two-four'])
	self.assertEqual(self.fixture[4], ['four-seven', 'one-five',
					   'two-four'])
	self.assertEqual(self.fixture[8], [])
	self.assertEqual(self.fixture[15], ['fifteen-twenty'])
	self.assertEqual(self.fixture[17], ['fifteen-twenty'])
	self.assertEqual(self.fixture[20], ['fifteen-twenty'])
	self.assertEqual(self.fixture[28], [])

    def test_delitem(self):
        self.assertRaises(KeyError, self.fixture.__delitem__, (13, 20))
        del self.fixture[15, 20]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertEqual(self.fixture[1, 5], 'one-five')
        self.assertEqual(self.fixture[2, 4], 'two-four')
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[1, 5]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertEqual(self.fixture[2, 4], 'two-four')
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[2, 4]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (2, 4))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[4, 7]
        self.assertRaises(KeyError, self.fixture.__getitem__, (4, 7))
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (2, 4))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))

    def test_setslice(self):
	self.empty_fixture[4:7] = 'four-seven'
	self.empty_fixture[1:5] = 'one-five'
	self.empty_fixture[15:20] = 'fifteen-twenty'
	self.empty_fixture[2:4] = 'two-four'
        self.assertEqual(self.empty_fixture, self.fixture)

    def test_getslice(self):
	self.assertEqual(self.empty_fixture[1:10], [])
	self.assertRaises(ValueError, self.fixture.__getitem__, slice(5, 0))
	self.assertEqual(self.fixture[8:10], [])
	self.assertEqual(self.fixture[25:100], [])
	self.assertEqual(self.fixture[15:20], ['fifteen-twenty'])
	self.assertEqual(self.fixture[4:7],
                         ['four-seven', 'one-five', 'two-four'])
	self.assertEqual(self.fixture[1:7],
                         ['four-seven', 'one-five', 'two-four'])
	self.assertEqual(self.fixture[0:1], ['one-five'])
	self.assertEqual(self.fixture[20:25], ['fifteen-twenty'])
	self.assertEqual(self.fixture[6:16],
                         ['four-seven', 'fifteen-twenty'])
	self.assertEqual(self.fixture[7:15],
                         ['four-seven', 'fifteen-twenty'])

    def test_delslice(self):
        self.assertRaises(KeyError, self.fixture.__delitem__, slice(13, 20))
        del self.fixture[15:20]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertEqual(self.fixture[1, 5], 'one-five')
        self.assertEqual(self.fixture[2, 4], 'two-four')
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[1:5]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertEqual(self.fixture[2, 4], 'two-four')
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[2:4]
        self.assertEqual(self.fixture[4, 7], 'four-seven')
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (2, 4))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))
        del self.fixture[4:7]
        self.assertRaises(KeyError, self.fixture.__getitem__, (4, 7))
        self.assertRaises(KeyError, self.fixture.__getitem__, (1, 5))
        self.assertRaises(KeyError, self.fixture.__getitem__, (2, 4))
        self.assertRaises(KeyError, self.fixture.__getitem__, (15, 20))

    def test_has_key(self):
	self.failIf(self.empty_fixture.has_key(5))
	self.failIf(self.empty_fixture.has_key(1, 10))
	self.assertRaises(TypeError, self.empty_fixture.has_key, 1, 5, 10)
	self.assert_(self.fixture.has_key(1))
	self.assert_(self.fixture.has_key(6))
	self.assert_(self.fixture.has_key(18))
	self.assert_(self.fixture.has_key(4, 7))
	self.assert_(self.fixture.has_key(1, 5))
	self.assert_(self.fixture.has_key(15, 20))
	self.assert_(self.fixture.has_key(2, 4))
	self.failIf(self.fixture.has_key(1, 6))
	self.failIf(self.fixture.has_key(16, 19))
	self.failIf(self.fixture.has_key(0))
	self.failIf(self.fixture.has_key(8))
	self.failIf(self.fixture.has_key(26))
	self.failIf(self.fixture.has_key(-5, 0))
	self.failIf(self.fixture.has_key(8, 12))
	self.failIf(self.fixture.has_key(21, 24))
	self.assertRaises(TypeError, self.fixture.has_key, 1, 5, 10)

    def test_lists(self):
	self.assertEqual(self.empty_fixture.keys(), [])
	self.assertEqual(self.fixture.keys(), [(1, 5), (2, 4), (4, 7),
					       (15, 20)])
	self.assertEqual(self.empty_fixture.values(), [])
	self.assertEqual(self.fixture.values(), ['one-five',
						 'two-four',
						 'four-seven',
						 'fifteen-twenty'])
	self.assertEqual(self.empty_fixture.items(), [])
	self.assertEqual(self.fixture.items(), [((1, 5), 'one-five'),
						((2, 4), 'two-four'),
						((4, 7), 'four-seven'),
						((15, 20), 'fifteen-twenty')])

if __name__ == '__main__':
    unittest.main()
