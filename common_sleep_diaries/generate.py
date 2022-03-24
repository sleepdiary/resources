#!/usr/bin/env python3
#
# Sleep diary generator - create files containing common sleep diaries
# Written in 2022 by Andrew Sayers <sleepdiary@pileofstuff.org>
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

import common_sleep_diaries
import sys

sys.stderr.write(common_sleep_diaries.reproducibility_information())

def save_diary( name, diary ):
    f = open(f"{name}.csv", "w")
    f.write(common_sleep_diaries.diary_to_csv(diary)+"\n")
    f.close()

save_diary("simple"       , common_sleep_diaries.diary_simple())
save_diary("weekday_alarm", common_sleep_diaries.diary_weekday_alarm())
save_diary("dspd"         , common_sleep_diaries.diary_dspd())
save_diary("non24"        , common_sleep_diaries.diary_non24())
