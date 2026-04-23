import ledger

# Regression test for GitHub issue #752:
# `post.amount.value(eur)` applied to an EUR amount annotated with a GBP
# per-unit price (e.g. `-5.00 EUR {0.8733 GBP}`) used to return the amount
# unchanged, with its annotation intact.  Adding that result to an
# unannotated `0.00 EUR` accumulator then raised
#   ArithmeticError: Adding amounts with different commodities: EUR != EUR
# because the annotated and unannotated EUR commodities compared unequal.
#
# amount_t::value() now strips the annotation when the source commodity's
# referent matches the requested target commodity, so accumulating mixed
# annotated/unannotated EUR values via value() works as expected.

eur = ledger.commodities.find_or_create('EUR')

total = ledger.Amount("0.00 EUR")

journal = ledger.read_journal_from_string("""
D 1000.00 EUR
P 2011-01-01 GBP 1.2 EUR

2011-01-01 * Opening balance
    Assets:Bank                    10.00 GBP
    Equity:Opening balance

2012-01-02 * Test
    Assets:Bank                      5.00 GBP
    Income:Whatever

2012-01-03 * Test
    Assets:Bank
    Income:Whatever              -5.00 EUR @  0.8733 GBP
""")

for post in journal.query("^income:"):
    a = post.amount.value(eur)
    assert a is not None, "value(eur) should return a converted amount"
    assert not a.has_annotation(), \
        "value() must strip annotation when target commodity matches referent"
    total += a

print("total = %s" % total)
