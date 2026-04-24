import ledger

# Regression test for GitHub issue #1796:
# Access posting flags in Python.
#
# Originally, reading post.flags or calling post.has_flags(ITEM_GENERATED)
# raised Boost.Python.ArgumentError because the JournalItem binding bound
# the flag getters/setters to supports_flags<uint_least8_t>, while item_t
# actually inherits from supports_flags<uint_least16_t>.  The type mismatch
# made every flags-related method unreachable from Python.
#
# Fixed alongside issue #2169 by binding the uint_least16_t specialisation
# in py_item.cc.  This test exercises the exact call sites reported in the
# issue to guard against the type mismatch returning.

session = ledger.Session()
j = session.read_journal_from_string("""
2024/01/01 Lunch
    Expenses:Food          $10.00
    Assets:Cash           $-10.00

2024/01/02 Virtual tracking
    (Virtual:Envelope)     $25.00
    Expenses:Supplies      $25.00
    Assets:Cash           $-25.00
""")

for xact in j:
    # Both JournalItem.flags (property) and JournalItem.has_flags (method)
    # must be callable from Python without raising ArgumentError.
    print("xact flags=%d has_flags(ITEM_GENERATED)=%s"
          % (xact.flags, xact.has_flags(ledger.ITEM_GENERATED)))
    for post in xact.posts:
        name = post.account.fullname()
        print("  post %s: flags=%d has_flags(ITEM_GENERATED)=%s has_flags(POST_VIRTUAL)=%s"
              % (name, post.flags,
                 post.has_flags(ledger.ITEM_GENERATED),
                 post.has_flags(ledger.POST_VIRTUAL)))

# Mutating methods (add_flags, drop_flags, clear_flags) must round-trip too.
first_post = next(iter(next(iter(j)).posts))
first_post.add_flags(ledger.ITEM_GENERATED)
print("after add_flags: has_flags(ITEM_GENERATED)=%s"
      % first_post.has_flags(ledger.ITEM_GENERATED))
first_post.drop_flags(ledger.ITEM_GENERATED)
print("after drop_flags: has_flags(ITEM_GENERATED)=%s"
      % first_post.has_flags(ledger.ITEM_GENERATED))
