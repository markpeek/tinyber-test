
from coro.asn1.ber import *
from t0_test import try_decode

# this will auto-generate test cases - both good and bad ones - to exhaustively
#  cover the tinyber codec generated for t0.asn.
# currently generates 3000+ tests.

def gen_pair():
    return [
        (SEQUENCE (INTEGER (10), INTEGER (101)), True),
        # out of range integer
        (SEQUENCE (INTEGER (10), INTEGER (10)), False),
        (SEQUENCE (INTEGER (1001), INTEGER (10)), False),
        # unwanted negative integer
        (SEQUENCE (INTEGER (-5), INTEGER (-6)), False),
        # junk
        ('asdfasdfasdf', False),
        ('\xDE\xAD\xBE\xEF', False),
        ('x', False),
        # trailing junk
        (SEQUENCE (INTEGER (10), INTEGER (101), 'asdfasdf'), False),
        (SEQUENCE (INTEGER (10), INTEGER (101), BOOLEAN(True)), False),
    ]

def gen_color():
    return [
        (ENUMERATED (0), True),
        (ENUMERATED (1), True),
        (ENUMERATED (2), True),
        (ENUMERATED (3), False),
        (ENUMERATED (4), False),
        # bad type
        (INTEGER (99), False),
        # junk
        ('wieuriuwiusdf', False),
        ('x', False),
        ]
    
def gen_msgb():
    return [
        (SEQUENCE (INTEGER (1001), BOOLEAN(True), SEQUENCE()), True),
        (SEQUENCE (INTEGER (1<<30), BOOLEAN(True), SEQUENCE()), True),
        (SEQUENCE (INTEGER (1001), BOOLEAN(False), SEQUENCE()), True),
        # exactly one x
        (SEQUENCE (INTEGER (1001), BOOLEAN(False), SEQUENCE(BOOLEAN(True))), True),
        # exactly two x
        (SEQUENCE (INTEGER (1001), BOOLEAN(False), SEQUENCE(BOOLEAN(True), BOOLEAN(False))), True),
        # too many x
        (SEQUENCE (INTEGER (1001), BOOLEAN(False), SEQUENCE(BOOLEAN(True), BOOLEAN(False), BOOLEAN(True))), False),
        # extra data
        (SEQUENCE (INTEGER (1001), BOOLEAN(False), SEQUENCE(), BOOLEAN(True), OCTET_STRING ("asdfasdfasdfasdfasdfasdfasdfasdfasdf")), False),
        (SEQUENCE (BOOLEAN(False), BOOLEAN(True)), False),
        (INTEGER (99), False),
        ('ksdjfkjwekrjasdf', False),
        ('x', False),
        ]

def gen_msga():
    result = []
    for pair, good_pair in gen_pair():
        for color, good_color in gen_color():
            result.extend ([
                # -- potentially good data ---
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (50), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), good_pair and good_color),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (51), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), good_pair and good_color),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (52), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(True), color), good_pair and good_color),
                # --- known to be bad data ---
                # not enough entries
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (52), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair), BOOLEAN(True), color), False),
                # bad first type
                (SEQUENCE (INTEGER (99), INTEGER (50), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), False),
                # out of range integers...
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (410), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), False),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (53), INTEGER (16555), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), False),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (54), INTEGER (10001), INTEGER (1<<33), SEQUENCE (pair,pair,pair,pair), BOOLEAN(False), color), False),
                # bad type in SEQUENCE OF
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (55), INTEGER (16555), INTEGER (99), SEQUENCE (INTEGER(99)), BOOLEAN(False), color), False),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (56), INTEGER (16555), INTEGER (99), INTEGER (99), BOOLEAN(False), color), False),
                # bad type in place of BOOLEAN
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (57), INTEGER (10001), INTEGER (398234234), SEQUENCE (pair,pair,pair,pair), INTEGER(-9), color), False),
                # negative integers in unexpected places
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (58), INTEGER (10001), INTEGER (-1000), SEQUENCE (pair,pair,pair), BOOLEAN(True), color), False), 
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (59), INTEGER (-100), INTEGER (-1000), SEQUENCE (pair,pair,pair), BOOLEAN(True), color), False),
                (SEQUENCE (OCTET_STRING ('abc'), INTEGER (-20), INTEGER (-100), INTEGER (-1000), SEQUENCE (pair,pair,pair), BOOLEAN(True), color), False),
            ])

    return result

def gen_thingmsg():
    result = []
    for msgb, good in gen_msgb():
        result.append ((TLV (APPLICATION (1), msgb), good),)
        # wrong tag
        result.append ((TLV (APPLICATION (0), msgb), False),)
    for msga, good in gen_msga():
        result.append ((TLV (APPLICATION (0), msga), good),)
        # bad tag
        result.append ((TLV (APPLICATION (9), msga), False),)
        # wrong tag
        result.append ((TLV (APPLICATION (1), msga), False),)


    return result
        
class ExpectedGood (Exception):
    pass
class ExpectedBad (Exception):
    pass
class BadEncoding (Exception):
    pass

def go():
    for tval, good in gen_thingmsg():
        print tval.encode ('hex')
        r = try_decode (tval)
        if not good:
            if r != -1:
                # it should have been bad, but wasn't.
                raise ExpectedBad
        elif r == -1:
            # it should have been good, but wasn't.
            raise ExpectedGood
        elif r != tval:
            # it was a good decode, but the encoding wasn't identical.
            raise BadEncoding
        else:
            # it's all good.
            pass

go()