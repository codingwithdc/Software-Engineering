from hypothesis import given, strategies as st
from restaurant_bill_parser import clean_dish_name, parse_item_prices, split_amount

@given(st.text() | st.none())
def test_clean_dish_name_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_parse_item_prices_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_split_amount_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass
