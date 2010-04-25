#!/usr/bin/perl

open IN, "compositions_short.txt";
open BEFORE, "> compositions_short_before";
open IBEFORE, "> compositions_short_ibefore";
open AFTER, "> compositions_short_after";
open IAFTER, "> compositions_short_iafter";

while (<>)
{
	print IBEFORE "if X $1 Y and Y $2 Z then X m Z\n" if /^(\S+) *\t(\S+) *\tm *$/;
	print BEFORE if /^(\S+) *\t(\S+) *\t\< *$/;
	print AFTER if /^(\S+) *\t(\S+) *\t\> *$/;
	print IAFTER if /^(\S+) *\t(\S+) *\tmi *$/;
}
