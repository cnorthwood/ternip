import pstats
import sys

profile = sys.argv[1]

p = pstats.Stats(profile)


#p.sort_stats('name').print_stats()

# The first call will actually sort the list by function name, and the
# second call will print out the statistics. The following are some
# interesting calls to experiment with:


p.sort_stats('cumulative').print_stats(20)

# This sorts the profile by cumulative time in a function, and then
# only prints the ten most significant lines. If you want to
# understand what algorithms are taking time, the above line is what
# you would use.


# If you were looking to see what functions were looping a lot, and
# taking a lot of time, you would do:

p.sort_stats('time').print_stats(10)

