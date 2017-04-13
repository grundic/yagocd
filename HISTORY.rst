.. :changelog:

Release History
---------------

1.0.0 (2017-04-13)
++++++++++++++++++

**Improvements**
- Added elastic profile support.
- Added package repositories API support.
- Added package management API support.
- Added encryption API support.
- Improvements in `ValueStreamMap`.
- Added enumerations (constants) for stage result and state.
- Reworked artifact manager (breaking change!)
- ETag is now part of resource object (breaking change!)

**Miscellaneous**
- Added support for 16.11.0 version.
- Added support for 17.01.0 version.
- Added support for 17.02.0 version.
- Added support for 17.03.0 version.
- Refactored managers urls and parameters.

0.4.4 (2016-12-01)
++++++++++++++++++

**Improvements**
- Client's manager are now initialized just once, which makes possible to cache the results of their calls.

0.4.3 (2016-11-23)
++++++++++++++++++

**Improvements**
- Improvements in `ValueStreamMap`.
- Added possibility to programmatically disable version check in `Since` decorator, using `ENABLED` flag.

**Miscellaneous**
- Added support for 16.10.1 version.

0.4.2 (2016-10-28)
++++++++++++++++++

**Improvements**
- ValueStreamMap: put dictionary instead of StageInstance.

0.4.1 (2016-10-09)
++++++++++++++++++

**Improvements**
- Added custom exception error, which outputs error in clear format.
- Added support for pluggable SCM materials API.
- Added support for template API.
- Improvements in `ValueStreamMap`.

**Miscellaneous**
- Documentation updated.
- Docker image updated, which used in testing.
- Added support for 16.10.0 version.

0.4.0 (2016-10-01)
++++++++++++++++++

**Improvements**

- Added support for pipeline config API.
- Added support for version API.
- Added support for plugin info API.
- Added support for environments API.
- Added methods for getting different internal information (undocumented): `support` and `process_list`.
- Added magic methods for iterating and key based access for some classes.
- All classes and their methods are now decorated with `@since` decorator, which adds possibility to check
  at run-time whether given functionality already supported in the GoCD server and let's dynamically select
  correct headers.

**Testing**

- Now tests are executed for GoCD version, running in Docker container, which add possibility
  to test for any available version of the server. Also cassettes are also saved individually for
  each GoCD version.
- Added testing for PEP8 and other checks via `flake8`.

0.3.2 (2016-07-26)
++++++++++++++++++

**Improvements**

- Added support of `value_stream_map` functionality.

**Bugfixes**

- Fix return value of `Artifact.fetch` method from text to binary.

0.2.0 (2016-05-24)
++++++++++++++++++

**Improvements**

- Added support of getting server version through parsing `/about` page.
- Added `Confirm: true` header to some API calls.

