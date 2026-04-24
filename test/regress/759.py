import ledger

# Regression test for GitHub issue #759:
# Allow comparing a Commodity with a string directly, e.g.
#     if post.amount.commodity == "EUR":
# as a convenient shortcut for
#     if post.amount.commodity.symbol == "EUR":

session = ledger.Session()
j = session.read_journal_from_string("""
2024-01-01 Coffee
    Expenses:Food    10.00 EUR
    Assets:Cash     -10.00 EUR

2024-01-02 Lunch
    Expenses:Food    $15.00
    Assets:Cash     -$15.00
""")

for xact in j:
    for post in xact.posts:
        c = post.amount.commodity
        eq_eur = c == "EUR"
        ne_eur = c != "EUR"
        print(f"{post.account.fullname()}: symbol={c.symbol!r} == 'EUR' -> {eq_eur}, != 'EUR' -> {ne_eur}")
