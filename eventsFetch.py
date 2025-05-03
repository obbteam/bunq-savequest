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
    'X-Bunq-Client-Request-Id': 'X4py9CcDP13MlQ7w56L2',
    'X-Bunq-Geolocation': '0 0 0 0 000',
    'X-Bunq-Client-Authentication': 'aa37199c853288faa7716ee4668b7d6c34b1c479e37a565853657672fb06e7e3',
    'X-Bunq-Client-Signature': 'KvLNmlJV0fQO0LKi1nvdDZ1n4VW9iREMlGAys5AHSd+ORK4GCLVj413iWBAKGr/+cjunN9csCpIYZy5z7L3AHNcaMxlT3cq8N6EkY97LR1cgQodcSS7Tpg75i0avLENM9331KgtY0XLMfNmOv54LkqD3SnKbbNx32LgfkRzk1XqF3/cfTgLSsJ8yil5+W8D83jAqC7edDb1IJ9aYOADCl/Ghn/UMpYJFnOJOj0IwZVdLBWiUymjkk+rYPIGottorTeyxJDOiqZ2xEzj9xcxigq+71lXmpbV0j+HCNSXMYyAiqygoutGk9MkAOa0EPB1EfKeayt0PxYGAfpMfB9htSg=='
    }
    conn.request("GET", "/v1/user/1882847/event?count=200", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = json.loads(data.decode("utf-8"))

    events_by_category = {}

    if "Response" in response:
        for event in response["Response"]:

            if 'object' in event['Event']:
                event_object = event['Event']['object']


                if ('RequestInquiry' in event_object) and (event["Event"]["status"] == "FINALIZED" or "ACCEPTED"):
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
                        events_by_category["INCOME"] = {
                            "event_list": [],
                            "total": 0.0
                        }

                    events_by_category["INCOME"]["event_list"].append(event_entry)
                    events_by_category["INCOME"]["total"] += float(request_inquiry["amount_responded"]["value"])

                elif ('Payment' in event_object) and (event["Event"]["status"] == "FINALIZED" or "ACCEPTED"):
                    print("payment valid")
                    categoryName = event_object["Payment"]["description"]
                    try:
                        start = categoryName.index("CATEGORY:") + len("CATEGORY:")
                        end = categoryName.find(",", start)
                        categoryName = categoryName[start:end].strip()
                    except:
                        categoryName = "invalid"

                    event_entry = {
                        "ID": event["Event"]["id"],
                        "DATE": event["Event"]["created"],
                        "DESC": event_object["Payment"]["description"],
                        "AMOUNT": event_object["Payment"]["amount"]['value'],
                        "COUNTRY": event_object["Payment"]["alias"]["country"],
                        "CURRENCY": event_object["Payment"]["amount"]['currency']
                    }
                    if categoryName not in events_by_category:
                        events_by_category[categoryName] = {
                            "event_list": [],
                            "total": 0.0
                        }

                    #ASSUMING EURO USAGE
                    events_by_category[categoryName]["event_list"].append(event_entry)
                    events_by_category[categoryName]["total"] += float(event_object["Payment"]["amount"]['value'])

            print("\n---\n")
        else:
            print("no object found")
    else:
        print("No events found.")

    with open("events_by_category.json", "w", encoding="utf-8") as f:
        json.dump(events_by_category, f, ensure_ascii=False, indent=4)

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

class myCategories(Enum):
    GENERAL = "FAMILY"
    SUBSCRIPTIONS = "TRAVEL"
    CASH = "CASH"
    SAVINGS = "FOOD & DRINKS"
    FINANCE = "FINANCE"


# for i in range(1,3):
#     createPayment("RENT_AND_UTILITIES", i*50, f"more transaction for RENT_AND_UTILITIES, number:{i}")