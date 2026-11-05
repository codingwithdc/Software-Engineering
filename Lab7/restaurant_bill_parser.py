def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Returns an empty string for None, non-string or blank input.
    """
    if not isinstance(name, str):
        return ""
    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')
    return name.strip().title()

def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of ints.
    Blank entries are skipped. Returns an empty list if the input is
    not a string or any price is not a non-negative whole number.
    """
    if not isinstance(text, str):
        return []
    prices = []
    for part in text.split(','):
        part = part.strip()
        if part == "":
            continue
        try:
            price = int(part)
        except ValueError:
            return []
        if price < 0:
            return []
        prices.append(price)
    return prices

def split_amount(text):
    """
    Splits 'TOTAL/PEOPLE' into the amount each person pays.
    Returns None if the input is not a string, is not in TOTAL/PEOPLE
    form, has non-whole-number values, a negative total, or people <= 0.
    """
    if not isinstance(text, str):
        return None
    parts = text.split('/')
    if len(parts) != 2:
        return None
    try:
        total = int(parts[0])
        people = int(parts[1])
    except ValueError:
        return None
    if total < 0 or people <= 0:
        return None
    return total // people

def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    dish = clean_dish_name(value)
    print("Dish name:", dish if dish else "Invalid dish name")

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    prices = parse_item_prices(value)
    print("Item prices:", prices if prices else "Invalid prices")

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    share = split_amount(value)
    print("Each person pays:", share if share is not None else "Invalid input, use TOTAL/PEOPLE with people > 0")

if __name__ == "__main__":
    main()
