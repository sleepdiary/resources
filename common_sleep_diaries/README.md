# Public diary datasets

Computer-generated datasets for use in sleep diary applications.  All files are provided under [the CC0 license](https://creativecommons.org/share-your-work/public-domain/cc0/), so are available for use without restriction.

These diaries have been produced using [a Python program](generate.py), which guarantees to generate the same data each time it is run on the same platform.  The output should be identical to the available datasets below when run on a system where the `reproducibility_information()` function returns the following:

```
Version of Common Sleep Diaries: 0.0.1
Version of Python: 3.9.12 (main, Mar 24 2022, 13:02:21) ; [GCC 11.2.0]
Implementation: namespace(name='cpython', cache_tag='cpython-39', version=sys.version_info(major=3, minor=9, micro=12, releaselevel='final', serial=0), hexversion=50924784, _multiarch='x86_64-linux-gnu')
```

If your system returns different `reproducibility_information`, you can see whether the output is the same by comparing the output of [`generate.py`](generate.py) on your system with the available datasets below.

Available datasets:

* [A diary that resembles someone with no interesting sleep issues](simple.csv)
* [A diary that resembles someone who sets an alarm for 7am on weekdays](weekday_alarm.csv)
* [A diary that resembles someone who has Delayed Sleep Phase Disorder](dspd.csv)
* [A diary that resembles someone who has Non-24 Sleep-Wake Disorder](non24.csv)

These datasets only provide a basic resemblance to each condition, and are primarily intended for use in testing new software.

Available software:

* [a library to generate datasets](common_sleep_diaries.py)
* [an example program using the library](example.py)
* [the program used to generate the datasets above](generate.py)

## License

<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/p/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="https://sleepdiary.github.io/resources/">
    <span property="dct:title">Sleep Diary Authors</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Sleep Diary Resources</span>.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
      content="GB" about="https://sleepdiary.github.io/resources/">
  United Kingdom</span>.
</p>