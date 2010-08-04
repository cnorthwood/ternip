#!/usr/bin/env python

import unittest
from ternip import timex
from ternip.rule_engine.normalisation_functions import *

class date_functions_Test(unittest.TestCase):
    
    def test_normalise_two_year_date_full(self):
        self.assertEquals('1989', normalise_two_digit_year('1989'))
    
    def test_normalise_two_year_date_full_just_year(self):
        self.assertEquals('1989', normalise_two_digit_year('19890101'))
    
    def test_normalise_two_year_date_apostrophe(self):
        self.assertEquals('1992', normalise_two_digit_year("'92"))
    
    def test_normalise_two_year_date_apostrophe_future(self):
        self.assertEquals('2018', normalise_two_digit_year("'18"))
    
    def test_normalise_two_year_date_two_year(self):
        self.assertEquals('1992', normalise_two_digit_year("92"))
    
    def test_normalise_two_year_date_two_year_future(self):
        self.assertEquals('2018', normalise_two_digit_year("18"))
    
    def test_normalise_two_year_date_first_millenium(self):
        self.assertEquals('0906', normalise_two_digit_year('906'))
    
    def test_easter_date_string(self):
        self.assertEquals('20100404', easter_date('2010'))
    
    def test_easter_date_int(self):
        self.assertEquals('20100404', easter_date(2010))
    
    def test_date_to_week(self):
        self.assertEquals('2010W31', date_to_week(2010, 8, 3))
    
    def test_date_to_dow_normal(self):
        self.assertEquals(2, date_to_dow(2010, 8, 3))
    
    def test_date_to_dow_wraparound(self):
        self.assertEquals(0, date_to_dow(2010, 8, 1))
    
    def test_nth_dow_to_date_normal(self):
        self.assertEquals(3, nth_dow_to_date(8, 2, 1, 2010))
    
    def test_nth_dow_to_date_special_case(self):
        self.assertEquals(8, nth_dow_to_date(8, 7, 2, 2010))
    
    def test_nth_dow_to_date_special_case2(self):
        self.assertEquals(12, nth_dow_to_date(7, 1, 2, 2010))

class string_conversions_Test(unittest.TestCase):
    
    def test_month_to_num_abbr(self):
        self.assertEquals(4, month_to_num('apr'))
    
    def test_month_to_num_full(self):
        self.assertEquals(4, month_to_num('April'))
    
    def test_month_to_num_mixed(self):
        self.assertEquals(6, month_to_num('JUNE'))
    
    def test_month_to_num_invalid(self):
        self.assertEquals(0, month_to_num('Frentober'))
    
    def test_day_to_num_full(self):
        self.assertEquals(0, day_to_num('sunday'))
    
    def test_month_to_num_mixed(self):
        self.assertEquals(5, day_to_num('FRIDAY'))
    
    def test_month_to_num_mixed(self):
        self.assertEquals(7, day_to_num('frankfurter'))
    
    def test_decade_num(self):
        self.assertEquals(9, decade_nums('nine'))
    
    def test_decade_num_mixed(self):
        self.assertEquals(8, decade_nums('EiGH'))
    
    def test_decade_num_bad(self):
        self.assertEquals(1, decade_nums('twenty-seven'))
    
    def test_season(self):
        self.assertEquals('SP', season('spring'))
    
    def test_season_mixed(self):
        self.assertEquals('WI', season('WINTER'))
    
    def test_season_bad(self):
        self.assertEquals('hunting', season('hunting'))
    
    def test_units_to_gran(self):
        self.assertEquals('D', units_to_gran('day'))
    
    def test_units_to_gran_mixed(self):
        self.assertEquals('C', units_to_gran('CENTURY'))
    
    def test_units_to_gran_bad(self):
        self.assertEquals('bad', units_to_gran('bad'))
    
    def test_fixed_holiday_date(self):
        self.assertEquals('1225', fixed_holiday_date('christmas'))
    
    def test_fixed_holiday_date_mixed(self):
        self.assertEquals('0423', fixed_holiday_date('<Saint~NNP><George~NNP>'))
    
    def test_fixed_holiday_date_bad(self):
        self.assertEquals('', fixed_holiday_date('bad'))
    
    def test_nth_dow_holiday_date(self):
        self.assertEquals((1, 1, 3), nth_dow_holiday_date('king'))
    
    def test_nth_dow_holiday_date_mixed(self):
        self.assertEquals((11, 4, 4), nth_dow_holiday_date('ThanksGiving'))
    
    def test_nth_dow_holiday_date_bad(self):
        self.assertEquals((0,0,0), nth_dow_holiday_date('bad'))

class words_to_num_Test(unittest.TestCase):
    
    def test_ordinal_number(self):
        self.assertEquals(6, ordinal_to_num('6th'))
    
    def test_ordinal_word(self):
        self.assertEquals(18, ordinal_to_num('eighteenth'))
    
    def test_ordinal_bad(self):
        self.assertEquals(1, ordinal_to_num('beefburger'))
    
    def test_words_to_num_simple(self):
        self.assertEquals(8, words_to_num("eight"))
    
    def test_words_to_num_none(self):
        self.assertEquals(0, words_to_num(None))
    
    def test_words_to_num_a(self):
        self.assertEquals(100, words_to_num('a hundred'))
    
    def test_words_to_num_the(self):
        self.assertEquals(6, words_to_num('the six'))
    
    def test_words_to_num_and(self):
        self.assertEquals(326, words_to_num('three hundred and twenty six'))
    
    def test_words_to_num_and(self):
        self.assertEquals(7320, words_to_num('seven thousand, three hundred and twenty'))
    
    def test_words_to_num_mixed(self):
        self.assertEquals(1806, words_to_num('18 hundred and six'))
    
    def test_words_to_num_mixed(self):
        self.assertEquals(324, words_to_num('324'))
    
    def test_words_to_num_mixed(self):
        self.assertEquals(0, words_to_num('six hundred and bread'))
    
    def test_words_to_num_ordinal(self):
        self.assertEquals(92, words_to_num('ninety second'))
    
    def test_words_to_num_bad_ordinal(self):
        self.assertEquals(0, words_to_num('first two'))