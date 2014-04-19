234218-wet1-tests
=================
How-To:
-------
1. set environment variable WET1_EXEC to path to wet1 exec file
 * on Linux: export WET1_EXEC=/path/to/exec
 * on Windows: http://www.computerhope.com/issues/ch000549.htm
2. run simple_tests.py
3. (optional, Linux only) to enable valgrind checks set WET1_VALGRIND env variable to 1.

The tests generate a directory with all the outputs in test-output/simple/YYYYMMDDHHMMSS/, the following files are created:

1. Wet1TestCases-commands-NUM input of the test NUM
2. Wet1TestCases-out-actual-NUM output of the provided exec to test NUM
3. Wet1TestCases-out-expected-NUM output that was expected for thest NUM
4. Wet1TestCases-valgrind-NUM valgrind report of memory leaks if valgrind enabled (for test NUM)
