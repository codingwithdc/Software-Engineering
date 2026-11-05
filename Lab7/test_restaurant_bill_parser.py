from hypothesis import given, strategies as st
from restaurant_bill_parser import clean_dish_name, parse_item_prices, split_amount

@given(st.text() | st.none())
def test_clean_dish_name_no_crash(s):
    try:
        clean_dish_name(s)
    except Exception as e:
        assert False, f"clean_dish_name crashed with input {s!r}: {e}"

@given(st.text() | st.none())
def test_parse_item_prices_no_crash(s):
    try:
        parse_item_prices(s)
    except Exception as e:
        assert False, f"parse_item_prices crashed with input {s!r}: {e}"

@given(st.text() | st.none())
def test_split_amount_no_crash(s):
    try:
        split_amount(s)
    except Exception as e:
        assert False, f"split_amount crashed with input {s!r}: {e}"
