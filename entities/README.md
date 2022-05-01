# entities.json specification

[`entities.json`](../entities.json) is a [JSON](https://www.json.org/) file containing information about sleep-related entities.  This document explains the format of that file.

The project itself builds [`entities.json`](../entities.json) from files hosted in the same directory as this specification.  Their format is typically similar enough that an interested developer can learn a lot from the specification, but no guarantees are made about them - even that they will continue to exist in future.  Production systems should avoid them in favour of [`entities.json`](../entities.json) itself.

## Common features

All versions of [`entities.json`](../entities.json) contain a single root object with a `format` key that uniquely identifies the file format.  The associated value MUST begin with `https://sleepdiary.github.io/resources/entities#`, followed by an arbitrary string.  All versions of the format so far use [semantic versioning](https://semver.org/), but implementations should not depend on this behaviour.  Instead, implementations that handle more than one version should check the format string against a list of known values.

## Version 0.0.1

Format string: `https://sleepdiary.github.io/resources/entities#version-001`

Contains the following top-level sections:

- `valid_values` - lists of values that are allowed for certain keys
- `specialist` - doctors and researchers that examine sleep
- `software` - programs to process sleep data

### `valid_values`

This object contains a set of key/value pairs, where each key indicates the name of a key that can exist elsewhere in the document, and each value is an object describing valid values for that key.  Depending on the key, valid values might be either a single string or an array of strings from the list.

The following example says that all `specialist_type` keys outside of `valid_values` must have a string value matching either `physician` or `researcher`.  It further includes a non-normative English description for what those keys mean.

```json
{
 ...
 "specialist_type": {
   "physician": "a medical doctor who treats sleep disorders",
   "researcher": "an academic who studies sleep disorders"
 }
 ...
}
```

### `specialist`

This object contains a single `records` key, the value of which is a list of known specialists.  Each entry in the list is an object with the following keys:

- `name` - _(object)_ name of the specialist
  - see [sort keys](#sort-keys), below
- `description` - _(markdown string)_ short description of the specialist
- `admin_contact` - _(plain-text string)_ how to contact the specialist about changes to their information
- `specialist_type` - _(plain-text string)_ see `specialist_type` in `valid_values`
- `last_updated` - _(plain-text string)_ - date of last update, in the form `YYYY-MM-DD`
- `procedure_type` - _(plain-text string)_ see `procedure_type` in `valid_values`
- `url` - _(plain-text string)_ URL of the specialist's front page
- `referral_types` - _(array of plain-text strings)_ see `referral_types` in `valid_values`
- `registration_required` - _(boolean value)_ whether the specialist requires individuals to register
- `registration_tel` - _(optional plain-text string)_ - telephone number for individuals to register
- `registration_fax` - _(optional plain-text string)_ - fax number for individuals to register
- `registration_url` - _(optional plain-text string)_ - URL for individuals to register
- `registration_other` - _(optional plain-text string)_ - other information about the registration process
- `booking_required` - _(boolean value)_ whether the specialist requires individuals to book appointments
- `booking_tel` - _(optional plain-text string)_ - telephone number for individuals to book appointments
- `booking_fax` - _(optional plain-text string)_ - fax number for individuals to book appointments
- `booking_url` - _(optional plain-text string)_ - URL for individuals to book appointments
- `booking_other` - _(optional plain-text string)_ - other information about the booking process
- `appointment_types` - _(array of plain-text strings)_ see `appointment_types` in `valid_values`
- `appointment_type_other` - _(optional markdown string)_ information about the `other` appointment type
- `before_first` (markdown string) - actions individuals should take before attending their first appointment
- `between_appointments` (markdown string) - actions individuals should take between appointments
- `outcomes` - _(array of plain-text strings)_ see `outcomes` in `valid_values`
- `outcome_other` - _(optional markdown string)_ information about the `other` outcome type
- `locations` (array of objects) - information about locations where the specialist operates
  - see [`locations`](#locations), below
- `forms` - _(array of objects)_ - information about forms that individuals may need to fill out
  - see [`forms` and `reports`](#forms-and-reports), below
- `reports` (array of objects) - information about reports that individuals may be shown
  - see [`forms` and `reports`](#forms-and-reports), below

#### `locations`

Each entry in the `locations` array contains the following values:

- `display_name` - _(plain-text string)_ Full name of the location
  - includes BOTH organisation AND location name
- `short_name` - _(plain-text string)_ Short name of the location
  - includes EITHER organisation OR location name
- `has_name` - _(boolean value)_ whether `display_name` and `short_name` include the location name
- `address` - _(plain-text string)_ street address of the location
- `gps` - _(pair of plain-text strings)_ latitude and longitude of the location
- `tel` - _(optional plain-text string)_ telephone number of the location
- `fax` - _(optional plain-text string)_ fax number of the location
- `url` - _(optional plain-text string)_ URL of the location
- `referral_types` - _(array of plain-text strings)_ see `referral_types` in `valid_values`

#### `forms` and `reports`

Each entry in the `forms` and `reports` arrays contain the following values:

- `display_name` - _(plain-text string)_ Full name of the document
  - includes BOTH organisation AND document name
- `short_name` - _(plain-text string)_ Short name of the document
  - includes EITHER organisation OR document name
- `has_name` - _(boolean value)_ whether `display_name` and `short_name` include the document name
- `doc_type` - _(plain-text string)_ either `form` or `report`
  - intended for use by functions that accept entries from both `forms` and `reports`
- `url` - _(plain-text string)_ URL of the document
- `instructions_to_find` - _(markdown string)_ How to find this form organically
- `use_before_first` - _(plain-text string)_ see `use_before_first` in `valid_values`
- `use_between_appointments` - _(plain-text string)_ see `use_between_appointments` in `valid_values`
- `layout` - _(plain-text string)_ type of form or report
- `sharing_status` - _(plain-text string)_ see `sharing_status` in `valid_values`
- `start_page` - _(integer)_ one-based index of the first page in the PDF containing this document
  - for example, a PDF might have a map, a discussion of common conditions, then a sleep diary
- `total_pages` - _(integer)_ number of pages in the PDF dedicated to this document
- `thumb` - _(plain-text string)_ URL of a thumbnail for this document
  - can be an absolute URL or relative to the site that `entities.json` is hosted on
- `gallery` - _(array of objects)_ - images of this document
  - see [`gallery`](#gallery), below

The following entries are only relevant for entries with a `layout` of `calendar`:

- `inbed_marker` - _(markdown string)_ how the calendar marks getting into bed
- `outofbed_marker` - _(markdown string)_ how the calendar marks getting out of bed
- `sleep_marker` - _(markdown string)_ how the calendar marks periods of sleep
- `page_duration` - _(object)_ how much time is represented by a single page
  - see [sort keys](#sort-keys), below
- `start_time` - _(object)_ left-most time in the calendar (e.g. midnight or 6pm)
  - see [sort keys](#sort-keys), below
- `events` - _(array of objects)_ - specific events marked in this calendar
  - see [`events`](#events), below

#### `gallery`

Each entry in the `gallery` array contains an image of the document, contaning the following values:

- `display_name` - _(plain-text string)_ Full name of the image
  - includes BOTH document AND image name
- `short_name` - _(plain-text string)_ Short name of the image
  - includes EITHER document OR image name
- `has_name` - _(boolean value)_ whether `display_name` and `short_name` include the image name
- `thumb` - _(plain-text string)_ URL of a thumbnail for this image
  - can be an absolute URL or relative to the site that `entities.json` is hosted on
- `url` - _(plain-text string)_ URL of the image
  - can be an absolute URL or relative to the site that `entities.json` is hosted on

#### `events`

Each entry in the `events` array contains an event that should be marked in a calendar.  For example, marking caffeine consumption.  Each entry is an object containing the following values:

- `key` - _(markdown string)_ how the calendar marks this event
- `value` - _(plain-text string)_ meaning of this event

#### sort keys

Some values are hard to sort correctly.  For example, most algorithms will not sort the list `[ "6am", "noon", "10pm" ]` in a useful order.  Sort keys are objects that resemble the following:

```json
{
  "key": "012345",
  "value": "hard-to-sort-string"
}
```

`key` is a string to sort on.  Some sort keys only contains digits, but should not be converted to integers because the leading `0`s are significant.

`value` is a value to display.

### `software`

This section will be documented in an upcoming version.  The contents of the file are likely to change during that process.
