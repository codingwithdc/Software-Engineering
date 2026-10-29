import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# =====================================================================
# bill_total
# Decisions:
#   D1  section not in SERVICE_CHARGE        (True -> error / False)
#   D2  food_total < 0 or guests < 1          (True -> error / False)
#   D3  is_happy_hour and section != takeaway (True -> 20% off / False)
#   D4  guests >= 8                           (True -> +200 / False)
# =====================================================================

def test_dine_in_bill():
    # D3 False (no happy hour), D4 False: 1000 + 100 = 1100, + 55 tax = 1155
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_unknown_section_raises():
    # D1 True
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_negative_food_total_raises():
    # D2 True via first condition (food_total < 0)
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_zero_guests_raises():
    # D2 True via second condition (guests < 1)
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 1000, 0, False)


def test_zero_food_total_is_valid():
    # D2 False at the boundary food_total == 0
    assert bill_total("dine_in", 0, 1, False) == 0


def test_happy_hour_dine_in():
    # D3 True: 1000 -> 800, service 80, total 880, + 44 tax = 924
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_happy_hour_takeaway_no_discount():
    # D3 False even though is_happy_hour is True (section == takeaway)
    # 1000, service 0, + 50 tax = 1050
    assert bill_total("takeaway", 1000, 2, True) == 1050


def test_rooftop_no_happy_hour():
    # 15% service: 1000 + 150 = 1150, + 57 tax = 1207
    assert bill_total("rooftop", 1000, 2, False) == 1207


def test_rooftop_happy_hour():
    # D3 True on rooftop: 800, service 120, total 920, + 46 tax = 966
    assert bill_total("rooftop", 1000, 2, True) == 966


def test_large_party_surcharge():
    # D4 True at boundary guests == 8: service 100 + 200, total 1300, + 65 = 1365
    assert bill_total("dine_in", 1000, 8, False) == 1365


def test_seven_guests_no_surcharge():
    # D4 False just below boundary (guests == 7)
    assert bill_total("dine_in", 1000, 7, False) == 1155


def test_takeaway_large_party_surcharge():
    # D4 True with 0% service: service 0 + 200, total 1200, + 60 tax = 1260
    assert bill_total("takeaway", 1000, 8, False) == 1260


# =====================================================================
# split_bill
# Decisions:
#   D5  people < 1                 (True -> error / False)
#   D6  tip_percent < 0            (True -> error / False)
#   D7  grand_total % people != 0  (True -> round up / False)
# =====================================================================

def test_even_split():
    # D7 False: 1000 + 100 tip = 1100, / 4 = 275
    assert split_bill(1000, 4, 10) == 275


def test_zero_people_raises():
    # D5 True
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_negative_tip_raises():
    # D6 True
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 4, -5)


def test_zero_tip_is_valid():
    # D6 False at boundary tip_percent == 0; D7 False
    assert split_bill(99, 3, 0) == 33


def test_single_person_pays_all():
    # D5 False at boundary people == 1
    assert split_bill(1000, 1, 10) == 1100


def test_uneven_split_rounds_up():
    # D7 True: 100 / 3 = 33 r1 -> 34
    assert split_bill(100, 3, 0) == 34


# =====================================================================
# table_wait
# Decisions:
#   D8   party_size > 12                        (True -> call ahead / False)
#   D9   has_reservation                         (True -> seat now / False)
#   D10  free_tables == 0                        (True -> waitlist / False)
#   D11  party_size > 6 and free_tables < 2      (True -> waitlist / False)
# =====================================================================

def test_very_large_party_calls_ahead():
    # D8 True
    assert table_wait(13, 5, False) == "call ahead"


def test_very_large_party_with_reservation_still_calls_ahead():
    # D8 True takes priority over a reservation
    assert table_wait(13, 5, True) == "call ahead"


def test_party_of_twelve_not_call_ahead():
    # D8 False at boundary party_size == 12, then D9 True
    assert table_wait(12, 5, True) == "seat now"


def test_reservation_seats_now_even_with_no_tables():
    # D9 True
    assert table_wait(4, 0, True) == "seat now"


def test_no_free_tables_waitlist():
    # D9 False, D10 True
    assert table_wait(4, 0, False) == "waitlist"


def test_big_party_few_tables_waitlist():
    # D10 False, D11 True (7 > 6 and 1 < 2)
    assert table_wait(7, 1, False) == "waitlist"


def test_party_of_six_one_table_seated():
    # D11 False via first condition (party_size == 6 is not > 6)
    assert table_wait(6, 1, False) == "seat now"


def test_big_party_two_tables_seated():
    # D11 False via second condition (free_tables == 2 is not < 2)
    assert table_wait(7, 2, False) == "seat now"


def test_walk_in_seated():
    # D10 False, D11 False
    assert table_wait(4, 3, False) == "seat now"