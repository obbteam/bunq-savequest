import http.client
import json
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import PaymentApiObject
from bunq.sdk.model.generated.object_ import AmountObject, PointerObject
from enum import Enum
from collections import defaultdict

class Category(Enum):
    GENERAL = "GENERAL"
    SUBSCRIPTIONS = "SUBSCRIPTIONS"
    CASH = "CASH"
    SAVINGS = "SAVINGS"
    FINANCE = "FINANCE"
    FAMILY = "FAMILY"
    SHOPPING = "SHOPPING"
    ENTERTAINMENT = "ENTERTAINMENT"
    FOOD_AND_DRINK = "FOOD_AND_DRINK"
    GROCERIES = "GROCERIES"
    PERSONAL_CARE = "PERSONAL_CARE"
    HOUSEHOLD_EXPENSES = "HOUSEHOLD_EXPENSES"
    TRAVEL = "TRAVEL"
    BUSINESS_EXPENSES = "BUSINESS_EXPENSES"
    CAR_EXPENSES = "CAR_EXPENSES"
    UNCATEGORIZED = "UNCATEGORIZED"
    ELECTRONICS = "ELECTRONICS"
    INVESTMENTS = "INVESTMENTS"
    CULTURE = "CULTURE"
    HEALTHCARE = "HEALTHCARE"
    PETS = "PETS"
    CLOTHING = "CLOTHING"
    SPORTS = "SPORTS"
    GIFTS = "GIFTS"
    PAYROLL = "PAYROLL"
    HR = "HR"
    MARKETING = "MARKETING"
    RENT_AND_UTILITIES = "RENT_AND_UTILITIES"
    INSURANCE = "INSURANCE"
    EMPLOYEE_BENEFITS = "EMPLOYEE_BENEFITS"
    OFFICE_SUPPLIES = "OFFICE_SUPPLIES"
    ASSETS = "ASSETS"
    PROFESSIONAL_SERVICES = "PROFESSIONAL_SERVICES"
    INCOME = "INCOME"

api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)

conn = http.client.HTTPSConnection("public-api.sandbox.bunq.com")

def createPayment(category, amount, description):
    payment_id = PaymentApiObject.create(
    amount=AmountObject(str(amount), "EUR"),
    counterparty_alias=PointerObject("EMAIL", "sugardaddy@bunq.com"),
    description=f"CATEGORY:{category}, {description}").value
    print(f"Payment created with ID: {payment_id}")


def fetchEvents():
    payload = ''
    headers = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'User-Agent': 'postman',
    'X-Bunq-Language': 'en_US',
    'X-Bunq-Region': 'nl_NL',
    'X-Bunq-Client-Request-Id': '6M7MfZ536OlX5i8s9a-p',
    'X-Bunq-Geolocation': '0 0 0 0 000',
    'X-Bunq-Client-Authentication': '382b71ab621b04b54626d4ed133c6ae9686e56f103a88ff8781880be7ccc41b8',
    'X-Bunq-Client-Signature': 'VnS3Rb6ydNPqr2f0IMk0H2KYzncvhnzD3wT8gr18al2eYsZomeQEHOdlxdQU+j8fd6c8h40WKRvI7e2rWgGG3wXwYw8hgufF5CsbKT0udO31NAy3/oUq2PiZWqLsXc3XujCxyBgyKWb278OWOBMo9f1YheBgue1zHrhfX/NxuMEKEWidFSq6Sg8dz7/NFGR5Y27Jpl1ID3QpUQo0UEh2Iq4kNpnF41U+KYH9dvysApZqoDC4DRCt3rkyAdCUsAdX5Ts1p3HwFfourmoEXza03Q7YMOv3cYxFJN+tj7uQPjOG3K9SKRYfgPaQEveQnpXdJA+kHR/p5u+lRj/ypZQg2g=='
    }
    conn.request("GET", "/v1/user/1879655/event", payload, headers)


    res = conn.getresponse()
    data = res.read()
    response = json.loads(data.decode("utf-8"))

    events_by_category = {}

    if "Response" in response:
        for event in response["Response"]:
    

            if 'object' in event['Event']:
                event_object = event['Event']['object']
                if 'RequestInquiry' in event_object and event_object["RequestInquiry"]["status"] == "FINALIZED":
                    request_inquiry = event_object['RequestInquiry']

                    event_entry = {
                        "ID": event["Event"]["id"],
                        "DATE": event["Event"]["created"],
                        "DESC": request_inquiry["description"],
                        "AMOUNT": request_inquiry["amount_responded"]["value"],
                        "COUNTRY": request_inquiry["user_alias_created"]["country"],
                        "CURRENCY": request_inquiry["amount_responded"]["currency"]
                    }
                    if "INCOME" not in events_by_category:
                        events_by_category["INCOME"] = []

                    events_by_category["INCOME"].append(event_entry)

                elif 'Payment' in event_object:
                    categoryName = event_object["Payment"]["description"]
                    start = categoryName.index("CATEGORY:") + len("CATEGORY:")
                    end = categoryName.find(",", start)
                    categoryName = categoryName[start:end].strip()

                    event_entry = {
                        "ID": event["Event"]["id"],
                        "DATE": event["Event"]["created"],
                        "DESC": event_object["Payment"]["description"],
                        "AMOUNT": event_object["Payment"]["amount"]['value'],
                        "COUNTRY": event_object["Payment"]["alias"]["country"],
                        "CURRENCY": event_object["Payment"]["amount"]['currency']
                    }
                    if categoryName not in events_by_category:
                        events_by_category[categoryName] = []

                    events_by_category[categoryName].append(event_entry)
            print("\n---\n")
    else:
        print("No events found.")
    print(events_by_category)

#createPayment(Category.UTILITIES.value, 50, "car maintenance")

CATEGORY_KEYWORDS = {
    "FOOD": ["FOOD", "mcdonald", "pizza", "restaurant", "burger", "kfc"],
    "TRAVEL": ["TRAVEL", "uber", "train", "ns", "flixbus", "airbnb"],
    "ENTERTAINMENT": ["ENTERTAINMENT", "netflix", "spotify", "cinema", "amusement"],
}

def categorize(description):
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in desc for keyword in keywords):
            return category
    return "GENERAL"

def analyze_events(events):
    analysis = {
        "Total_income": 0.0,
        "Total_outcome": 0.0,
        "Total_category": defaultdict(float)
    }

    for event in events:
        if 'Payment' in event:
            payment = event['Payment']
            amount = float(payment['amount']['value'])
            description = payment.get('description', '')

            if amount > 0:
                analysis["Total_income"] += amount
            else:
                analysis["Total_outcome"] += abs(amount)
                category = categorize(description)
                analysis["Total_category"][category] += abs(amount)

    # Convert defaultdict to dict for output
    analysis["Total_category"] = dict(analysis["Total_category"])
    return {"Analysis": analysis}

fetchEvents()

for category in Category:
    for i in range(5):
        createPayment(category.value, (i+1)*0.5, f"test transaction for{category.value}, number:{i}")
