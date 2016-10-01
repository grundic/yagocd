.. :changelog:

Release History
---------------

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

