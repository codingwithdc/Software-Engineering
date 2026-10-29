import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# ---------- bill_total ----------

def test_dine_in_bill():
    # 1000 + 10% service = 1100, + 5% tax = 1155
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_unknown_section_raises():
    # covers line 6
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_negative_food_total_raises():
    # covers line 8
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_happy_hour_dine_in():
    # covers line 10: 1000 -> 800, service 80, total 880, + tax 44 = 924
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_large_party_surcharge():
    # covers line 13: service 100 + 200 = 300, total 1300, + tax 65 = 1365
    assert bill_total("dine_in", 1000, 8, False) == 1365


# ---------- split_bill ----------

def test_even_split():
    # 1000 + 10% tip = 1100, / 4 = 275
    assert split_bill(1000, 4, 10) == 275


def test_zero_people_raises():
    # covers line 20
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_negative_tip_raises():
    # covers line 22
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 4, -5)


def test_uneven_split_rounds_up():
    # covers line 26: 100 / 3 = 33 r1 -> 34
    assert split_bill(100, 3, 0) == 34


# ---------- table_wait ----------

def test_very_large_party_calls_ahead():
    # covers lines 31-32
    assert table_wait(13, 5, False) == "call ahead"


def test_reservation_seats_now():
    # covers lines 33-34
    assert table_wait(4, 0, True) == "seat now"


def test_no_free_tables_waitlist():
    # covers lines 35-36
    assert table_wait(4, 0, False) == "waitlist"


def test_big_party_few_tables_waitlist():
    # covers lines 37-38
    assert table_wait(8, 1, False) == "waitlist"


def test_walk_in_seated():
    # covers line 39
    assert table_wait(4, 3, False) == "seat now"