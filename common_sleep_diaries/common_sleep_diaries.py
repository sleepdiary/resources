# Common sleep diaries - automatically-generated diaries depicting various sleeping conditions
# Written in 2022 by Andrew Sayers <sleepdiary@pileofstuff.org>
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

"""automatically-generated diaries depicting various sleeping conditions

Reproducibility
===============

This diary should generate the same results on each run, and those results
should only change minimally when the program is updated.
But see "Limits of reproducibilty" below.

To ensure the same output between runs, we need to make our pseudo-random number
generator give us the same set of numbers every time.  For example, each run
of the program should generate an identical set of "caffeine" events.

To avoid correlations between types of event, we need to make our pseudo-random
number generator give us an unrelated series of numbers for each event type.
For example, the series of "caffeine" events should have a different distribution
to the series of "dinner" events.

To ensure maintainability, we need the ability to add, change, or remove one
data series without affecting the others.  For example, the program should still
generate the same "caffeine" events even if we add a series of "sugar" events.

Python's pseudo-random number generator works by growing a series of numbers
from an initial "seed" value.  Each seed value leads to a different series of
random numbers, but a given seed value will produce the same series every time.

To achieve the goals above, this program generates one type of event at a time,
and switches to a new random seed before generating each type.

For more information, see the documentation for Python's `random` module:
* https://docs.python.org/3/library/random.html

Limits of reproducibility
=========================

This file can produce different results in different versions of Python.
We make heavy use of Python's `random` module, which is not guaranteed
to behave identically between versions, and indeed has changed behaviour
on at least two occasions.

If reproducibility is important for your use case, it is recommended to
publish the output of `reproducibility_information()` alongside your data.

See also:
* https://docs.python.org/3.3/library/random.html#notes-on-reproducibility
* https://stackoverflow.com/questions/8786084/reproducibility-of-python-pseudo-random-numbers-across-systems-and-versions

"""

import random
import datetime
import sys

#
# Utilities
#

__version__ = "0.0.1"

# Constants to make durations easier to read:
SECONDS =  1
MINUTES = 60*SECONDS
HOURS   = 60*MINUTES
DAYS    = 24*HOURS

# Unix timestamp for 2020-01-01T00:00:00Z:
START_DATE = 1577836800
# 2020-01-01T00:00:00Z is a Wednedsay:
START_DAY_OF_WEEK = datetime.datetime.fromtimestamp(START_DATE).weekday()
# Number of records to generate per diary:
TOTAL_SLEEPS = 365

def use_rng_dataset(a):
    """Cause the random number generator to start a new series of numbers

    Python's random number generator starts with an initial "random seed",
    then generates a predictable series of numbers based on that seed.
    In other words, the random seed acts somewhat like an index into a
    collection of ready-made datasets of random numbers."""
    random.seed(a)

def append_entry( entries, status, start, end = None, comments = "" ):
    """Create a new entry, if the event actually occurred"""
    if end is None:
        end = start
    if start is not None and start.actually_occurred and end.actually_occurred:
        entries.append({
            "key"     : start.value,
            "start"   : start.to_datetime(),
            "end"     : end  .to_datetime(),
            "status"  : status,
            "comments": comments,
        })

#
# Periods
#
# People are assumed to spend their time alternating between SleepPeriods and WakePeriods
#

class Event:
    """An event that (may have) occurred at an instant in time

    Events generally occur at a time relative to some other event,
    and the base event may not actually occur.  For example,
    a person's dinner time might be specified relative to their lunch time,
    whether or not the "lunch" event actually occurred.

    * `mu` and `sigma` are passed to random.normalvariate()
    * `probability` is the probability the event will actually occur
    * values outside the range `[minimum,maximum]` are reset to
      `minimum` or `maximum`.
    * if `before` or `after` are specified, `mu` will be treated as an offset
      from that time.  It is added to `after` or subtracted from `before`,
      to indicate e.g. an amount of time after waking up or before going to bed.
    """
    def __init__(
            self,
            mu, sigma, probability,
            minimum = None, maximum = None,
            before = None,
            after = None,
    ):
        if after is not None:
            mu = after + mu
        elif before is not None:
            mu = before - mu
        self.actually_occurred = random.random() <= probability
        self.value = random.normalvariate(mu,sigma)
        if minimum is not None and self.value < minimum:
            self.value = minimum
        if maximum is not None and self.value > maximum:
            self.value = maximum

    def to_datetime(self):
        """Create a datetime object at the time of this event"""
        return datetime.datetime.fromtimestamp(START_DATE+self.value)

class SleepPeriod:
    """A period of time where someone is trying to sleep"""
    def __init__(
            self,

            in_bed_mu        , in_bed_sigma,
            fall_asleep_mu   , fall_asleep_sigma,
            sleep_duration_mu, sleep_duration_sigma,
            alarm_mu         , alarm_sigma, alarm_probability,

            alarm_wake_mu, alarm_wake_sigma,
            out_of_bed_mu, out_of_bed_sigma
    ):

        # A constant to make this function easier to read:
        MAX_PROBABILITY = 1

        self.in_bed      = Event( in_bed_mu, in_bed_sigma, MAX_PROBABILITY )
        self.fall_asleep = Event(
            self.in_bed.value + fall_asleep_mu,
            fall_asleep_sigma,
            MAX_PROBABILITY,
            minimum=self.in_bed.value
        )
        self.alarm       = Event( in_bed_mu + alarm_mu, alarm_sigma, alarm_probability )

        if self.alarm.actually_occurred:
            wake_mu    = self.alarm.value       + alarm_wake_mu
            wake_sigma = alarm_wake_sigma
        else:
            wake_mu    = self.fall_asleep.value + sleep_duration_mu
            wake_sigma = sleep_duration_sigma
        self.wake_up = Event( wake_mu, wake_sigma, MAX_PROBABILITY )

        self.out_of_bed = Event(
            self.wake_up.value + out_of_bed_mu,
            out_of_bed_sigma,
            MAX_PROBABILITY
        )

        # Values set in later functions:
        self.lights_off  = None
        self.night_noise = None
        self.sleep_aid   = None

    def append_entries(self,entries):
        """Add all entries for this period"""
        append_entry( entries, "alarm"      , self.alarm )
        append_entry( entries, "asleep"     , self.fall_asleep, self.wake_up )
        append_entry( entries, "in bed"     , self.in_bed )
        append_entry( entries, "lights off" , self.lights_off )
        append_entry( entries, "night noise", self.night_noise )
        append_entry( entries, "out of bed" , self.out_of_bed )
        append_entry( entries, "sleep aid"  , self.sleep_aid )

    def set_lights_off( self, mu, sigma, probability = 1 ):
        """Set the 'lights off' event for this period"""
        self.lights_off = Event(
            self.in_bed.value - mu,
            sigma, probability,
            maximum=self.fall_asleep.value
        )

    def set_night_noise( self, mu, sigma, probability = 1 ):
        """Set the 'night noise' event for this period"""
        self.night_noise = Event(
            ( self.wake_up.value + self.fall_asleep.value ) / 2 + mu,
            sigma, probability,
            minimum=self.in_bed.value,
            maximum=self.out_of_bed.value
        )

    def set_sleep_aid( self, mu, sigma, probability = 1 ):
        """Set the 'sleep aid' event for this period

        Sleeping pills are the most common type of sleep aid, but this could also be e.g. a drink"""
        self.sleep_aid = Event(
            self.in_bed.value - mu,
            sigma, probability,
            maximum=self.in_bed.value
        )

class WakePeriod:
    """The time between two SleepPeriods"""
    def __init__(
            self,
            previous_sleep,
            next_sleep
    ):
        self.start = previous_sleep.out_of_bed
        self.end   =     next_sleep.in_bed

        # Values set in later functions:
        self.alcohol         = None
        self.bathroom        = []
        self.breakfast       = None
        self.breakfast_drink = None
        self.snack           = None
        self.caffeine        = None
        self.lunch           = None
        self.dinner          = None
        self.chocolate       = None

    def append_entries(self,entries):
        """Add all entries for this period"""
        append_entry( entries, "alcohol"  , self.alcohol )
        append_entry( entries, "meal"     , self.breakfast, comments="breakfast" )
        append_entry( entries, "caffeine" , self.caffeine )
        append_entry( entries, "chocolate", self.chocolate )
        append_entry( entries, "meal"     , self.dinner, comments="dinner" )
        append_entry( entries, "drink"    , self.breakfast_drink, comments="with breakfast" )
        append_entry( entries, "meal"     , self.lunch, comments="lunch" )
        append_entry( entries, "snack"    , self.snack )
        for entry in self.bathroom:
            append_entry( entries, "toilet", entry )

    def set_alcohol( self, *args, **kwargs ):
        """Set the 'alcohol' event for this period"""
        self.alcohol = Event(
            *args, **kwargs,
            before=self.end.value,
            minimum=self.start.value,
            maximum=self.end.value
        )

    def append_bathroom( self, *args, **kwargs ):
        """Add a 'bathroom' event for this period"""
        self.bathroom.append(
            Event(
                *args, **kwargs,
                after=self.start.value,
                minimum=self.start.value,
                maximum=self.end.value
            )
        )

    def set_breakfast( self, *args, **kwargs ):
        """Set the 'breakfast' event for this period"""
        self.breakfast = Event(
            *args, **kwargs,
            after=self.start.value,
            minimum=self.start.value+5*MINUTES,
            maximum=self.end.value
        )

    def set_breakfast_drink( self, *args, **kwargs ):
        """Set the 'breakfast drink' event for this period"""
        self.breakfast_drink = Event(
            *args, **kwargs,
            after=self.breakfast.value,
            minimum=self.start.value+5*MINUTES,
            maximum=self.end.value
        )

    def set_caffeine( self, *args, **kwargs ):
        """Set the 'caffeine' event for this period"""
        self.caffeine = Event(
            *args, **kwargs,
            after=self.start.value,
            minimum=self.start.value+5*MINUTES,
            maximum=self.end.value
        )

    def set_chocolate( self, *args, **kwargs ):
        """Set the 'chocolate' event for this period"""
        self.chocolate = Event(
            *args, **kwargs,
            after=self.start.value,
            minimum=self.start.value+5*MINUTES,
            maximum=self.end.value
        )

    def set_dinner( self, *args, **kwargs ):
        """Set the 'dinner' event for this period"""
        self.dinner = Event(
            *args, **kwargs,
            after=self.lunch.value,
            minimum=self.lunch.value+1*HOURS,
            maximum=self.end.value
        )

    def set_lunch( self, *args, **kwargs ):
        """Set the 'lunch' event for this period"""
        self.lunch = Event(
            *args, **kwargs,
            after=self.breakfast.value,
            minimum=self.breakfast.value+1*HOURS,
            maximum=self.end.value
        )

    def set_snack( self, *args, **kwargs ):
        """Set the 'snack' event for this period"""
        self.snack = Event(
            *args, **kwargs,
            after=self.start.value,
            minimum=self.start.value+5*MINUTES,
            maximum=self.end.value
        )

#
# Create diaries
#

def periods_to_entries( *args ):
    """Convert sets of SleepPeriod and WakePeriod objects to a sorted series of entries"""
    entries = []
    for period in args:
        for item in period:
            item.append_entries(entries)
    return sorted( entries, key=lambda e: e['key'] )

def diary_regular(
        weekday_alarm_probability = 0,
        weekend_alarm_probability = 0,
        constant_phase_delay = 0,
        recurring_phase_delay = 0,
):
    """Base function for diaries with a regular day/night cycle"""

    #
    # Generate sleep events
    #

    use_rng_dataset(100)
    sleep_periods = []
    for n in range( 0,TOTAL_SLEEPS ):
        if ( START_DAY_OF_WEEK + n ) % 7 < 5:
            alarm_probability = weekday_alarm_probability
        else:
            alarm_probability = weekend_alarm_probability
        in_bed_mu = n*DAYS + constant_phase_delay*HOURS + n*recurring_phase_delay*HOURS
        sleep_periods.append(
            SleepPeriod(
                in_bed_mu         = in_bed_mu, in_bed_sigma         = 1  *HOURS,
                fall_asleep_mu    = 0.5*HOURS, fall_asleep_sigma    = 0.5*HOURS,
                sleep_duration_mu = 8  *HOURS, sleep_duration_sigma = 1  *HOURS,
                alarm_mu          = 7  *HOURS, alarm_sigma          = 0,
                alarm_probability = alarm_probability,

                alarm_wake_mu = 3  *MINUTES, alarm_wake_sigma = 0   *HOURS,
                out_of_bed_mu = 0.5*HOURS  , out_of_bed_sigma = 0.25*HOURS,
            )
        )

    use_rng_dataset(101)
    for sleep in sleep_periods:
        sleep.set_lights_off( 0.1*HOURS, 0.25*HOURS )

    use_rng_dataset(102)
    for sleep in sleep_periods:
        sleep.set_night_noise( 0*HOURS, 2*HOURS, 0.25 )

    use_rng_dataset(103)
    for sleep in sleep_periods:
        sleep.set_sleep_aid( 1*HOURS, 0.25*HOURS, 0.5 )

    #
    # Generate wake events
    #

    wake_periods  = []

    use_rng_dataset(200)
    for n in range( 0,TOTAL_SLEEPS-1 ):
        wake_periods.append(WakePeriod(sleep_periods[n],sleep_periods[n+1]))

    use_rng_dataset(201)
    for wake in wake_periods:
        wake.set_alcohol( 4*HOURS, 1*HOURS, 0.1 )

    use_rng_dataset(202)
    for wake in wake_periods:
        for n in range(0,3):
            wake.append_bathroom( 8*HOURS, 4*HOURS, 0.25 )

    use_rng_dataset(203)
    for wake in wake_periods:
        wake.set_breakfast( 0.5*HOURS, 0.25*HOURS, 0.8 )

    use_rng_dataset(204)
    for wake in wake_periods:
        # guarantee to have two events occur at the same time,
        # so we can see how it affects legibility of the output:
        wake.set_breakfast_drink( 0, 0, 0.8 )

    use_rng_dataset(205)
    for wake in wake_periods:
        wake.set_caffeine( 4*HOURS, 4*HOURS, 0.8 )

    use_rng_dataset(206)
    for wake in wake_periods:
        wake.set_chocolate( 4*HOURS, 4*HOURS, 0.8 )

    use_rng_dataset(207)
    for wake in wake_periods:
        wake.set_lunch( 3*HOURS, 0.5*HOURS, 0.8 )

    use_rng_dataset(208)
    for wake in wake_periods:
        wake.set_dinner( 5*HOURS, 1*HOURS, 0.8 )

    use_rng_dataset(209)
    for wake in wake_periods:
        wake.set_snack( 8*HOURS, 3*HOURS, 0.8 )

    return periods_to_entries( sleep_periods, wake_periods )

def diary_simple():
    """A diary that resembles someone with no interesting sleep issues"""
    return diary_regular()

def diary_weekday_alarm():
    """A diary that resembles someone who sets an alarm for 7am on weekdays"""
    return diary_regular(weekday_alarm_probability=1)

def diary_dspd():
    """A diary that resembles someone who has Delayed Sleep Phase Disorder"""
    return diary_regular(constant_phase_delay=4)

def diary_non24():
    """A diary that resembles someone who has Non-24 Sleep-Wake Disorder"""
    return diary_regular(recurring_phase_delay=1)

def diary_to_csv(entries):
    """Convert the diary to a CSV string"""
    entries = map(
        lambda entry :
        f"{entry['start'].isoformat()}Z,{entry['end'].isoformat()}Z,{entry['status']},{entry['comments']}",
        entries
    )
    return "Start,End,Status,Comments\n" + "\n".join(entries)

def reproducibility_information():
    """These functions are only guaranteed to be reproducible between implementations where the following are all identical"""
    version = sys.version.replace("\n","; ")
    return f"Version of Common Sleep Diaries: {__version__}\nVersion of Python: {version}\nImplementation: {sys.implementation}\n"
