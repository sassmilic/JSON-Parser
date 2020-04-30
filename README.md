# JSON-Parser
A JSON parser with informative error messages

The motivation for this script came when I was dealing with a large JSON file (a TinyDB) that wasn't properly formatted. When loading a JSON you typically get an error like: "there's a problem with column 267,635", which isn't very informative. I wrote this script to better pinpoint the problem.

**NOTE:** Very minimal testing has been done (see doctests). Use with caution :)

### TODO
* completely refactor to use a stack
* related to above: read one character from file at a time; no loading entire file to memory
* migrate tests from docstrings to seperate file

Another note: No, this doesn't have anything to do with Chainlink.
