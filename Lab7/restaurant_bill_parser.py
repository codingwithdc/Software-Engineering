def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Assumes name is a non-empty string.
    """
    name = name.strip()
    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')
    return name.title()

def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of ints.
    Assumes every price is a whole number.
    """
    return [int(price) for price in text.split(',')]

def split_amount(text):
    """
    Splits 'TOTAL/PEOPLE' into the amount each person pays.
    Assumes both values are whole numbers and people is not zero.
    """
    total, people = text.split('/')
    return int(total) // int(people)

def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    print("Dish name:", clean_dish_name(value))

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    print("Each person pays:", split_amount(value))

if __name__ == "__main__":
    main()
