#!/usr/bin/env python3
#
# Common sleep diary example - shows how to use the associated library
# Written in 2022 by Andrew Sayers <sleepdiary@pileofstuff.org>
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import common_sleep_diaries
import sys

# If reproducibility is important for your use case, it is recommended to
# publish the value of `sys.implementation` alongside your data.  For example:
sys.stderr.write(common_sleep_diaries.reproducibility_information())

diary = common_sleep_diaries.diary_weekday_alarm()

# The diary is an array of entries, where each entry is a dictionary:
#for entry in diary: print(entry)

# The diary above contains many types of entry, most of which you probably don't need.
# But if we don't generate them all, the random number generator will calculate
# different values for the remaining entries.
# So you should remove uninteresting entries by filtering the output instead:
statuses_of_interest = [ "asleep", "in bed", "out of bed", ]
diary = filter( lambda entry: entry["status"] in statuses_of_interest, diary )

print(common_sleep_diaries.diary_to_csv(diary))
