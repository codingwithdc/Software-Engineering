"""Insurance premium calculator.

Quotes health, motor and life premiums, works out an applicant's age,
saves quotes to a log, imports partner policies from XML, downloads rate
tables, extracts claim archives, splits premiums into instalments and
computes renewal dates.
"""

import hmac
import os
import secrets
import ssl
import tarfile
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime

import defusedxml.ElementTree as ET

# Global quote book
QUOTES = {}
HOST = os.environ.get("PREMIUM_HOST", "127.0.0.1")
UNDERWRITER_TOKEN = os.environ.get("UNDERWRITER_TOKEN", "")
LOG_FILE = "premium_quotes.log"
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}

@dataclass
class Applicant:
    """Risk details of the person being quoted."""

    age: int
    smoker: bool = False
    claims: int = 0

def calculate_premium(policy_type, sum_insured, applicant, discounts=None):
    """Return the yearly premium for a policy, never below zero."""
    if policy_type not in BASE_RATES:
        raise ValueError(f"Unknown policy type: {policy_type}")
    if not isinstance(applicant.smoker, bool):
        raise TypeError("smoker must be True or False")
    if discounts is None:
        discounts = []

    premium = BASE_RATES[policy_type] + sum_insured * 0.002
    if applicant.age > 45:
        premium *= 1.5
    if applicant.smoker:
        premium *= 1.3
    premium += applicant.claims * 1000
    premium -= sum(discounts)
    return max(round(premium, 2), 0.0)

def age_from_dob(dob, today=None):
    """Return the age in full years for a date of birth in DD-MM-YYYY."""
    born = datetime.strptime(dob, "%d-%m-%Y").date()
    today = today or date.today()
    had_birthday = (today.month, today.day) >= (born.month, born.day)
    return today.year - born.year - (0 if had_birthday else 1)

def policy_number():
    """Return an unpredictable policy number like POL-123456."""
    return "POL-" + str(100000 + secrets.randbelow(900000))

def save_quote(name, premium):
    """Store a quote in the quote book and append it to the log file."""
    number = policy_number()
    while number in QUOTES:
        number = policy_number()
    QUOTES[number] = {"name": name, "premium": premium}
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{number},{name},{premium:.2f}\n")
    return number

def import_policies(xml_text):
    """Parse partner XML and return (type, age, sum) tuples."""
    root = ET.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        try:
            result.append((policy.get("type"), int(policy.get("age")), int(policy.get("sum"))))
        except (TypeError, ValueError):
            print("Skipping invalid policy row:", policy.attrib)
    return result

def fetch_rates(url):
    """Download a rate table over verified HTTPS only."""
    if not url.lower().startswith("https://"):
        raise ValueError("Only https:// URLs are allowed")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(url, context=ctx, timeout=10) as resp:  # nosec B310
        return resp.read()

def import_claim_documents(archive_path):
    """Safely extract a customer claim archive into claims_docs."""
    with tarfile.open(archive_path) as tar:
        tar.extractall("claims_docs", filter="data")

def monthly_instalment(premium, months=12):
    """Return the instalment for splitting a premium over some months."""
    if months <= 0:
        raise ValueError("months must be a positive number")
    return round(premium / months, 2)

def is_authorised(token):
    """Check an underwriter token in constant time."""
    if not UNDERWRITER_TOKEN:
        return False
    return hmac.compare_digest(token, UNDERWRITER_TOKEN)

def renewal_due(start, years=1):
    """Return the renewal date, moving 29 Feb to 28 Feb when needed."""
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    try:
        due = start_date.replace(year=start_date.year + years)
    except ValueError:
        due = start_date.replace(year=start_date.year + years, day=28)
    return due.strftime("%Y-%m-%d")

def print_quotes():
    """Print every saved quote."""
    print("===== Quote Book =====")
    for index, (number, quote) in enumerate(QUOTES.items(), start=1):
        print(index, number, quote["name"], "Rs.", quote["premium"])

def main():
    """Run a demo of the calculator."""
    young = Applicant(age=30)
    p1 = calculate_premium("health", 500000, young)
    p2 = calculate_premium("health", 500000, young)
    p3 = calculate_premium("motor", 800000, Applicant(age=50, smoker=False))
    p4 = calculate_premium("life", 100000, Applicant(age=25), [3000, 3000, 3000])
    print("Quote 1:", p1)
    print("Quote 2 (same customer details):", p2)
    print("Non-smoker aged 50:", p3)
    print("Life with stacked discounts:", p4)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(p3))
    print("Renewal due:", renewal_due("2025-03-15"))
    print("Leap-year renewal:", renewal_due("2024-02-29"))
    sample_xml = ("<policies>"
                  "<policy type='health' age='40' sum='300000'/>"
                  "<policy type='motor' age='abc' sum='1'/>"
                  "</policies>")
    print("Imported:", import_policies(sample_xml))
    print("Saved as:", save_quote("Kiran", p1))
    token = os.environ.get("UNDERWRITER_TOKEN", "")
    print("Authorised:", is_authorised(token))
    print("Server would listen on", HOST)
    print_quotes()

if __name__ == "__main__":
    main()
