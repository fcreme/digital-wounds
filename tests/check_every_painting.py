#!/usr/bin/env python3
"""Checks a driver log from tests/scripts/every_painting.txt against its expected file.

cd build-test && ./digital_wounds --script ../tests/scripts/every_painting.txt > every.log 2>&1
python3 ../tests/check_every_painting.py every.log ../tests/scripts/every_painting.expected

Every mismatch is listed; the last line says N of M passed. Exits 1 on any failure.
"""

import re
import sys

STATE = re.compile(
    r"DRIVER state (?P<label>\S+) near=(?P<near>\S+) view=(?P<view>\S+) "
    r"artist=(?P<artist>\S+) page=(?P<page>\d+)"
)


def read_states(log):
    states = {}
    for line in log.splitlines():
        match = STATE.search(line)
        if match:
            states[match["label"]] = match.groupdict()
    return states


def read_expected(text):
    rows = []
    for line in text.splitlines():
        if line.strip():
            pid, artist, page = line.split("\t")
            rows.append((pid, artist, int(page)))
    return rows


def check(log, expected_text):
    """Returns (passed count, total, list of failure messages)."""
    states = read_states(log)
    rows = read_expected(expected_text)
    failures = []
    passed = 0
    for pid, artist, page in rows:
        problems = []
        aimed = states.get(pid + "_aimed")
        opened = states.get(pid + "_open")
        closed = states.get(pid + "_closed")
        if aimed is None or opened is None or closed is None:
            problems.append("missing state lines")
        else:
            want_near = "%s(%s#%d)" % (pid, artist, page)
            if aimed["near"] != want_near:
                problems.append("near=%s, want %s" % (aimed["near"], want_near))
            if (opened["view"], opened["artist"], int(opened["page"])) != ("open", artist, page):
                problems.append(
                    "opened view=%s artist=%s page=%s, want open %s %d"
                    % (opened["view"], opened["artist"], opened["page"], artist, page)
                )
            if closed["view"] != "closed":
                problems.append("view=%s after Q, want closed" % closed["view"])
        if problems:
            failures.append("%s: %s" % (pid, "; ".join(problems)))
        else:
            passed += 1
    return passed, len(rows), failures


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], errors="replace") as f:
        log = f.read()
    with open(argv[2]) as f:
        expected = f.read()
    passed, total, failures = check(log, expected)
    for failure in failures:
        print("FAIL " + failure)
    print("%d of %d passed" % (passed, total))
    return 0 if passed == total and total > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
