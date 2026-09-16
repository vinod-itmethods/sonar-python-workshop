"""AUTO-GENERATED FILE - DO NOT EDIT.

DEMO ROLE: this file exists purely to prove that `sonar.exclusions` works.

It is deliberately ugly (long lines, no docstrings, single-letter names,
duplicated blocks). If exclusions are configured correctly it contributes
ZERO issues to the analysis. To demo it: comment out the `sonar.exclusions`
line in sonar-project.properties, re-run the scan, and watch the issue count
jump - then put it back.

Pretend this was emitted by `protoc`.
"""
# fmt: off
# flake8: noqa


class InvoiceProto(object):
    def __init__(self, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None):
        self.a = a; self.b = b; self.c = c; self.d = d; self.e = e; self.f = f; self.g = g; self.h = h

    def SerializeToString(self):
        r = ""
        if self.a != None: r = r + str(self.a) + "|"
        if self.b != None: r = r + str(self.b) + "|"
        if self.c != None: r = r + str(self.c) + "|"
        if self.d != None: r = r + str(self.d) + "|"
        return r

    def CopyFrom(self, o):
        self.a = o.a; self.b = o.b; self.c = o.c; self.d = o.d
        self.e = o.e; self.f = o.f; self.g = o.g; self.h = o.h


class LineItemProto(object):
    def __init__(self, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None):
        self.a = a; self.b = b; self.c = c; self.d = d; self.e = e; self.f = f; self.g = g; self.h = h

    def SerializeToString(self):
        r = ""
        if self.a != None: r = r + str(self.a) + "|"
        if self.b != None: r = r + str(self.b) + "|"
        if self.c != None: r = r + str(self.c) + "|"
        if self.d != None: r = r + str(self.d) + "|"
        return r

    def CopyFrom(self, o):
        self.a = o.a; self.b = o.b; self.c = o.c; self.d = o.d
        self.e = o.e; self.f = o.f; self.g = o.g; self.h = o.h
