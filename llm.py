import json

import requests
import os

from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)
promt = '''
You are an AI financial coach. Your task is to analyze a user's past 3 months of transactions and generate a JSON report with detailed savings advice, personalized challenges, and a motivation message. Your output must follow the exact JSON format described below.

VERY IMPORTANT:
- Your output MUST be valid JSON.
- DO NOT include any text outside the JSON.
- DO NOT include markdown or any explanation — ONLY the JSON block.

---
USER GOAL:

"Save 1000€ for a trip to Japan in 30 days"  
Income per month: 1000€  
Expenses per month: 850€ (current)  
The goal is currently **not achievable**. Your job is to help.

---

YOU WILL RECEIVE:

- A list of transactions (date, category, amount, weekday, description)
- A dictionary of national monthly average spending per category

---
food - 400
Transport - 270
Bars / cafés - 100
Entertainment - 150
Shopping - 120
subscriptions - 25
rental - 900 

---

YOUR TASKS:

1. **Analyze the user's spending behavior:**
   - Group all transactions by category
   - Count the number of transactions per category
   - Group by day of the week to detect repetitive spending days (e.g. always shopping on Saturdays, bars on Fridays)
   - Identify recurring behaviors or unhealthy patterns

2. **Detect overspending:**
   - For each category:
     - Group all transaction on 6 categories food, transport, Entertainment, Shopping, rental, subscriptions
     - Calculate the **total spent over all transaction**
     - Calculate the **user’s monthly average** in that category
     - Compare it to the national monthly average for that category
     - If user's monthly average > 10% above national average → mark it as overspent
     - For each overspent category, include:
       - category name
       - user monthly average
       - national average
       - € over average
       - % over average
     - Round all numeric values to 2 decimal places

3. **Make personalized recommendations:**
   - For each overspent category, explain the issue briefly and give a short advice
   - Maximum 3 recommendations

4. **Generate up to 3 personalized saving challenges:**
   - Each challenge must have:
     - title
     - condition (task to complete)
     - target (e.g. amount, behavior)
     - reward: XP, savings in €, or bonus (string)
     - explanation ("why this matters") — must relate to the Japan trip goal if possible

5. **Project possible monthly savings:**
   - Based on all challenges and their savings values, estimate how much the user can save in 1 month if they succeed in all
   - Include it in a separate block called `savings_projection`

6. **Add motivation:**
   Generate 15 short, punchy, and emotionally engaging phrases to keep a user invested in a personal saving challenge. These phrases should appear at the top of a savings app and act like dynamic micro-headlines that drive the user to continue saving money and completing daily challenges.

Do NOT make them generic motivational quotes. Instead, make them bold, clever, and behavior-provoking — like something you'd see in a fitness app, a gamified finance app, or a startup landing page.

Tone: bold, energetic, playful, slightly provocative (in a positive way). Each phrase should feel like a call to action or a nudge toward progress.
Max 7 words per phrase.

---

JSON OUTPUT FORMAT (strict)

```json
{
  "analysis_summary": {
    "overspending_categories": [
      {
        "category": "string",
        "user_monthly_spending": float,
        "national_average": float,
        "excess_euro": float,
        "excess_percent": float
      }
    ],
    "spending_patterns": [
      "string", "string"
    ]
  },
  "recommendations": [
    {
      "category": "string",
      "comment": "string",
      "user_monthly_spending": float,
      "national_average": float,
      "excess_euro": float,
      "excess_percent": float
    }
  ],
  "challenges": [
    {
      "title": "string",
      "condition": "string",
      "target": float or "string",
      "reward": {
        "xp": int,
        "savings_euro": float or "string",
        "bonus": "optional string"
      },
      "why": "string"
    }
  ],
  "savings_projection": {
    "potential_monthly_savings": float,
    "note": "This amount is estimated based on completing all current challenges."
  },
  "motivation": "string"
}

DATA:

}







'''


first_promt = """

today is 2025-05-02 (format: YYYY-MM-DD)
You are an AI financial coach

The user has the following savings goal:
- Goal: "{goal_name}" 
- Amount: {goal_amount}€
- Target date: {goal_target_date}
- Country: {location}
- Monthly income: {monthly_income}€

Netherlands: €1700

Germany: €1500

France: €1650

Belgium: €1550

Austria: €1450

Ireland: €1900

Denmark: €1750

Sweden: €1600

Finland: €1500

Spain: €1250

Portugal: €1150

Italy: €1350

Greece: €1000

Poland: €1000

Czechia: €1050

Tasks:

1. Calculate how many days remain until the target date  
2. Estimate the amount the user can realistically save each month , Use average monthly expenses in {location} to estimate how much the user can realistically save per month.  
Assume moderate spending , basically you just monthly income - everage for this country = approximately how much you can save per month , but if the monthly income less then everage just put 20% from monthly salary 

3. If the goal is realistic — return that  
4. If NOT realistic:
   - Calculate how many **days** the user will need to reach the goal at that monthly savings rate  
   - Suggest the exact **date** when the goal is realistically reachable

---

Return result in strict JSON format:

```json
{
  "is_goal_realistic": true or false,
  "days_available": int,
  "estimated_monthly_savings": float,
  "required_days_to_reach_goal": int,               // only if goal is not realistic
  "recommended_completion_date": "YYYY-MM-DD"       // only if goal is not realistic
}
"""
data_for_goal = """
- Goal: "Trip to Japan"
- Total amount needed: 1000€
- Target date: 2025-06-02 (format: YYYY-MM-DD)
- Country of residence: Netherlands
- Monthly income: 1000€

"""

data = """
{
  "RENT_AND_UTILITIES": {
    "event_list": [
      {
        "ID": 1,
        "DATE": "2025-02-25 00:00:00",
        "DESC": "CATEGORY:RENT_AND_UTILITIES, Monthly rent",
        "AMOUNT": "-708.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 2,
        "DATE": "2025-03-25 00:00:00",
        "DESC": "CATEGORY:RENT_AND_UTILITIES, Monthly rent",
        "AMOUNT": "-671.50",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 3,
        "DATE": "2025-04-25 00:00:00",
        "DESC": "CATEGORY:RENT_AND_UTILITIES, Monthly rent",
        "AMOUNT": "-686.50",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -2066.37
  },
  "INCOME": {
    "event_list": [
      {
        "ID": 4,
        "DATE": "2025-02-28 00:00:00",
        "DESC": "CATEGORY:INCOME, Monthly salary February",
        "AMOUNT": "1944.64",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 5,
        "DATE": "2025-03-31 00:00:00",
        "DESC": "CATEGORY:INCOME, Monthly salary March",
        "AMOUNT": "2047.29",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 6,
        "DATE": "2025-04-30 00:00:00",
        "DESC": "CATEGORY:INCOME, Monthly salary April",
        "AMOUNT": "2035.34",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": 6027.27
  },
  "GROCERIES": {
    "event_list": [
      {
        "ID": 7,
        "DATE": "2025-02-03 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-56.08",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 8,
        "DATE": "2025-02-10 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-64.13",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 9,
        "DATE": "2025-02-17 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-60.78",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 10,
        "DATE": "2025-02-24 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-64.70",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 11,
        "DATE": "2025-03-03 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-62.81",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 12,
        "DATE": "2025-03-10 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-59.95",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 13,
        "DATE": "2025-03-17 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-64.73",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 14,
        "DATE": "2025-03-24 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-63.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 15,
        "DATE": "2025-03-31 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-58.50",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 16,
        "DATE": "2025-04-07 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-59.55",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 17,
        "DATE": "2025-04-14 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-62.80",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 18,
        "DATE": "2025-04-21 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-59.11",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 19,
        "DATE": "2025-04-28 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Weekly groceries",
        "AMOUNT": "-56.91",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 40,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-22.18",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 48,
        "DATE": "2025-03-04 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-69.58",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 52,
        "DATE": "2025-03-08 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-56.02",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 62,
        "DATE": "2025-03-16 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-49.92",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 76,
        "DATE": "2025-03-29 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-22.17",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 83,
        "DATE": "2025-04-09 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-35.20",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 97,
        "DATE": "2025-04-24 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-61.10",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 99,
        "DATE": "2025-04-27 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Random Groceries",
        "AMOUNT": "-77.06",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 108,
        "DATE": "2025-02-12 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-25.62",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 122,
        "DATE": "2025-03-10 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-5.16",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 127,
        "DATE": "2025-04-13 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-42.56",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 129,
        "DATE": "2025-02-19 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-18.87",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 146,
        "DATE": "2025-03-08 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-9.88",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 151,
        "DATE": "2025-03-30 00:00:00",
        "DESC": "CATEGORY:GROCERIES, Extra groceries",
        "AMOUNT": "-28.40",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -1316.78
  },
  "SUBSCRIPTIONS": {
    "event_list": [
      {
        "ID": 20,
        "DATE": "2025-02-10 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Music streaming",
        "AMOUNT": "-12.99",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 21,
        "DATE": "2025-03-10 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Music streaming",
        "AMOUNT": "-12.99",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 22,
        "DATE": "2025-04-10 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Music streaming",
        "AMOUNT": "-12.99",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 37,
        "DATE": "2025-02-20 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-17.26",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 39,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-56.35",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 65,
        "DATE": "2025-03-17 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-70.85",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 70,
        "DATE": "2025-03-22 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-74.67",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 74,
        "DATE": "2025-03-25 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-21.85",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 75,
        "DATE": "2025-03-27 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-49.13",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 78,
        "DATE": "2025-03-30 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-25.89",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 84,
        "DATE": "2025-04-11 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-19.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 89,
        "DATE": "2025-04-17 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Random Subscriptions",
        "AMOUNT": "-17.47",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 105,
        "DATE": "2025-03-15 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-16.95",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 119,
        "DATE": "2025-03-18 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-35.94",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 133,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-43.91",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 140,
        "DATE": "2025-03-04 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-6.06",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 150,
        "DATE": "2025-04-17 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-16.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 153,
        "DATE": "2025-04-29 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-21.39",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 180,
        "DATE": "2025-04-15 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-46.29",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 191,
        "DATE": "2025-03-11 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-17.23",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 193,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:SUBSCRIPTIONS, Extra subscriptions",
        "AMOUNT": "-22.24",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -618.28
  },
  "TRAVEL": {
    "event_list": [
      {
        "ID": 23,
        "DATE": "2025-03-14 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Flight ticket AMS-ROM",
        "AMOUNT": "-320.00",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 32,
        "DATE": "2025-02-09 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Random Travel",
        "AMOUNT": "-19.42",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 36,
        "DATE": "2025-02-19 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Random Travel",
        "AMOUNT": "-52.62",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 46,
        "DATE": "2025-03-02 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Random Travel",
        "AMOUNT": "-34.96",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 101,
        "DATE": "2025-05-02 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Random Travel",
        "AMOUNT": "-23.47",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 102,
        "DATE": "2025-05-02 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Random Travel",
        "AMOUNT": "-7.98",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 103,
        "DATE": "2025-04-28 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-30.44",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 161,
        "DATE": "2025-02-25 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-30.61",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 164,
        "DATE": "2025-04-18 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-34.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 174,
        "DATE": "2025-04-24 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-13.75",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 183,
        "DATE": "2025-04-15 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-19.28",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 184,
        "DATE": "2025-03-31 00:00:00",
        "DESC": "CATEGORY:TRAVEL, Extra travel",
        "AMOUNT": "-41.68",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -628.67
  },
  "PETS": {
    "event_list": [
      {
        "ID": 24,
        "DATE": "2025-02-04 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-36.70",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 29,
        "DATE": "2025-02-06 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-39.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 35,
        "DATE": "2025-02-18 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-75.25",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 41,
        "DATE": "2025-02-27 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-28.60",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 56,
        "DATE": "2025-03-12 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-24.75",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 71,
        "DATE": "2025-03-23 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-20.09",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 79,
        "DATE": "2025-04-01 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-75.16",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 93,
        "DATE": "2025-04-21 00:00:00",
        "DESC": "CATEGORY:PETS, Random Pets",
        "AMOUNT": "-76.80",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 113,
        "DATE": "2025-04-13 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-18.61",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 117,
        "DATE": "2025-02-16 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-29.90",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 124,
        "DATE": "2025-02-23 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-24.88",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 126,
        "DATE": "2025-02-12 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-45.68",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 156,
        "DATE": "2025-02-18 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-45.50",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 194,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-14.63",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 198,
        "DATE": "2025-04-18 00:00:00",
        "DESC": "CATEGORY:PETS, Extra pets",
        "AMOUNT": "-5.88",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -561.89
  },
  "SPORTS": {
    "event_list": [
      {
        "ID": 25,
        "DATE": "2025-02-04 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-16.66",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 44,
        "DATE": "2025-02-28 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-15.47",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 59,
        "DATE": "2025-03-13 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-68.13",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 64,
        "DATE": "2025-03-17 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-22.96",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 69,
        "DATE": "2025-03-21 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-44.58",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 96,
        "DATE": "2025-04-22 00:00:00",
        "DESC": "CATEGORY:SPORTS, Random Sports",
        "AMOUNT": "-21.33",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 104,
        "DATE": "2025-03-15 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-14.19",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 112,
        "DATE": "2025-03-22 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-12.10",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 115,
        "DATE": "2025-04-14 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-46.93",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 118,
        "DATE": "2025-03-09 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-32.22",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 136,
        "DATE": "2025-03-06 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-12.16",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 142,
        "DATE": "2025-02-11 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-20.80",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 145,
        "DATE": "2025-02-17 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-13.04",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 157,
        "DATE": "2025-04-08 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-35.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 163,
        "DATE": "2025-03-13 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-14.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 200,
        "DATE": "2025-03-20 00:00:00",
        "DESC": "CATEGORY:SPORTS, Extra sports",
        "AMOUNT": "-38.91",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -428.95
  },
  "PERSONAL_CARE": {
    "event_list": [
      {
        "ID": 26,
        "DATE": "2025-02-05 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-12.67",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 28,
        "DATE": "2025-02-05 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-50.28",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 34,
        "DATE": "2025-02-16 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-17.20",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 55,
        "DATE": "2025-03-09 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-13.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 77,
        "DATE": "2025-03-30 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-10.31",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 81,
        "DATE": "2025-04-06 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Random Personal Care",
        "AMOUNT": "-36.77",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 107,
        "DATE": "2025-04-02 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-46.81",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 130,
        "DATE": "2025-02-08 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-14.45",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 139,
        "DATE": "2025-04-02 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-18.73",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 144,
        "DATE": "2025-04-12 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-47.27",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 147,
        "DATE": "2025-03-30 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-37.78",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 155,
        "DATE": "2025-04-23 00:00:00",
        "DESC": "CATEGORY:PERSONAL_CARE, Extra personal_care",
        "AMOUNT": "-34.85",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -340.49
  },
  "HOUSEHOLD_EXPENSES": {
    "event_list": [
      {
        "ID": 27,
        "DATE": "2025-02-05 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Random Household Expenses",
        "AMOUNT": "-12.25",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 50,
        "DATE": "2025-03-05 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Random Household Expenses",
        "AMOUNT": "-49.73",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 91,
        "DATE": "2025-04-17 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Random Household Expenses",
        "AMOUNT": "-72.68",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 132,
        "DATE": "2025-04-15 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-48.82",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 134,
        "DATE": "2025-02-25 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-6.12",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 135,
        "DATE": "2025-03-17 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-41.10",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 141,
        "DATE": "2025-02-27 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-19.77",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 143,
        "DATE": "2025-04-09 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-35.58",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 148,
        "DATE": "2025-03-15 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-32.28",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 158,
        "DATE": "2025-03-16 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-36.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 160,
        "DATE": "2025-04-29 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-35.48",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 175,
        "DATE": "2025-05-03 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-27.25",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 185,
        "DATE": "2025-04-08 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-42.38",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 195,
        "DATE": "2025-03-28 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-19.89",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 196,
        "DATE": "2025-04-03 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-7.80",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 197,
        "DATE": "2025-03-28 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-45.72",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 199,
        "DATE": "2025-04-17 00:00:00",
        "DESC": "CATEGORY:HOUSEHOLD_EXPENSES, Extra household_expenses",
        "AMOUNT": "-26.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -559.68
  },
  "FOOD_AND_DRINK": {
    "event_list": [
      {
        "ID": 30,
        "DATE": "2025-02-06 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Random Food And Drink",
        "AMOUNT": "-77.98",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 33,
        "DATE": "2025-02-09 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Random Food And Drink",
        "AMOUNT": "-8.44",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 53,
        "DATE": "2025-03-08 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Random Food And Drink",
        "AMOUNT": "-56.13",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 66,
        "DATE": "2025-03-18 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Random Food And Drink",
        "AMOUNT": "-59.89",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 67,
        "DATE": "2025-03-18 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Random Food And Drink",
        "AMOUNT": "-78.35",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 109,
        "DATE": "2025-04-16 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-8.30",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 111,
        "DATE": "2025-03-19 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-44.57",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 121,
        "DATE": "2025-02-09 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-33.54",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 137,
        "DATE": "2025-05-03 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-22.21",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 149,
        "DATE": "2025-04-09 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-22.33",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 169,
        "DATE": "2025-03-17 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-41.83",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 177,
        "DATE": "2025-02-03 00:00:00",
        "DESC": "CATEGORY:FOOD_AND_DRINK, Extra food_and_drink",
        "AMOUNT": "-40.03",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -493.6
  },
  "GIFTS": {
    "event_list": [
      {
        "ID": 31,
        "DATE": "2025-02-08 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-51.39",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 38,
        "DATE": "2025-02-22 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-56.61",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 42,
        "DATE": "2025-02-27 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-42.44",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 43,
        "DATE": "2025-02-28 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-39.41",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 72,
        "DATE": "2025-03-25 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-33.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 82,
        "DATE": "2025-04-08 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-54.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 100,
        "DATE": "2025-04-30 00:00:00",
        "DESC": "CATEGORY:GIFTS, Random Gifts",
        "AMOUNT": "-69.64",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 106,
        "DATE": "2025-02-19 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-34.05",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 123,
        "DATE": "2025-02-19 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-49.09",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 131,
        "DATE": "2025-03-06 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-9.63",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 152,
        "DATE": "2025-04-12 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-37.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 154,
        "DATE": "2025-02-11 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-46.43",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 167,
        "DATE": "2025-02-24 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-8.82",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 168,
        "DATE": "2025-04-09 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-33.48",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 170,
        "DATE": "2025-03-05 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-18.97",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 182,
        "DATE": "2025-04-03 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-28.90",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 188,
        "DATE": "2025-03-06 00:00:00",
        "DESC": "CATEGORY:GIFTS, Extra gifts",
        "AMOUNT": "-17.48",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -630.73
  },
  "ELECTRONICS": {
    "event_list": [
      {
        "ID": 45,
        "DATE": "2025-03-01 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-24.71",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 47,
        "DATE": "2025-03-04 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-42.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 54,
        "DATE": "2025-03-08 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-61.32",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 57,
        "DATE": "2025-03-12 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-62.15",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 58,
        "DATE": "2025-03-12 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-73.45",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 60,
        "DATE": "2025-03-13 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-50.67",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 61,
        "DATE": "2025-03-15 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-76.51",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 73,
        "DATE": "2025-03-25 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-38.86",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 85,
        "DATE": "2025-04-11 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-38.65",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 87,
        "DATE": "2025-04-15 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-12.34",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 88,
        "DATE": "2025-04-16 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-67.70",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 94,
        "DATE": "2025-04-22 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-54.64",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 98,
        "DATE": "2025-04-26 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Random Electronics",
        "AMOUNT": "-73.95",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 110,
        "DATE": "2025-03-02 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-16.93",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 114,
        "DATE": "2025-04-27 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-5.35",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 120,
        "DATE": "2025-03-08 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-26.98",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 125,
        "DATE": "2025-03-29 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-5.44",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 128,
        "DATE": "2025-04-18 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-11.66",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 162,
        "DATE": "2025-03-26 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-42.52",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 166,
        "DATE": "2025-03-02 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-26.29",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 179,
        "DATE": "2025-05-03 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-25.90",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 192,
        "DATE": "2025-03-15 00:00:00",
        "DESC": "CATEGORY:ELECTRONICS, Extra electronics",
        "AMOUNT": "-8.63",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -846.66
  },
  "SHOPPING": {
    "event_list": [
      {
        "ID": 49,
        "DATE": "2025-03-04 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Random Shopping",
        "AMOUNT": "-52.06",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 68,
        "DATE": "2025-03-19 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Random Shopping",
        "AMOUNT": "-14.63",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 116,
        "DATE": "2025-02-16 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Extra shopping",
        "AMOUNT": "-16.90",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 159,
        "DATE": "2025-04-14 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Extra shopping",
        "AMOUNT": "-13.63",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 171,
        "DATE": "2025-02-28 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Extra shopping",
        "AMOUNT": "-6.10",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 176,
        "DATE": "2025-03-06 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Extra shopping",
        "AMOUNT": "-34.52",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 178,
        "DATE": "2025-03-03 00:00:00",
        "DESC": "CATEGORY:SHOPPING, Extra shopping",
        "AMOUNT": "-41.18",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -179.02
  },
  "CASH": {
    "event_list": [
      {
        "ID": 51,
        "DATE": "2025-03-07 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-44.68",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 63,
        "DATE": "2025-03-16 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-6.46",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 80,
        "DATE": "2025-04-02 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-23.22",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 86,
        "DATE": "2025-04-15 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-65.60",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 90,
        "DATE": "2025-04-17 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-41.10",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 92,
        "DATE": "2025-04-21 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-26.39",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 95,
        "DATE": "2025-04-22 00:00:00",
        "DESC": "CATEGORY:CASH, Random Cash",
        "AMOUNT": "-16.61",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 138,
        "DATE": "2025-02-07 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-15.01",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 165,
        "DATE": "2025-04-03 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-24.90",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 172,
        "DATE": "2025-03-06 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-32.51",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 173,
        "DATE": "2025-02-12 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-23.65",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 181,
        "DATE": "2025-02-18 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-11.00",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 186,
        "DATE": "2025-04-14 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-45.37",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 187,
        "DATE": "2025-04-04 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-16.66",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 189,
        "DATE": "2025-04-10 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-33.20",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      },
      {
        "ID": 190,
        "DATE": "2025-03-10 00:00:00",
        "DESC": "CATEGORY:CASH, Extra cash",
        "AMOUNT": "-8.49",
        "COUNTRY": "NL",
        "CURRENCY": "EUR"
      }
    ],
    "total": -434.85
  }
"""

def goal_promt(first_promt, data_for_goal):
  client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
  )
  completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    messages=[{"role": "system", "content": first_promt + data_for_goal}],
    temperature=0.6,
    top_p=0.95,
    max_tokens=4096,
    frequency_penalty=0,
    presence_penalty=0,
    stream=True
  )

  for chunk in completion:
    if chunk.choices[0].delta.content is not None:
      print(chunk.choices[0].delta.content, end="")

def transaction_promt(goal_name, amount, due_date, income):
  location = "Netherlands"
  m_promt = f"""

  today is 2025-05-02 (format: YYYY-MM-DD)
  You are an AI financial coach

  The user has the following savings goal:
  - Goal: "{goal_name}" 
  - Amount: {amount}€
  - Target date: {due_date}
  - Country: {location}
  - Monthly income: {income}€

  Netherlands: €1700

  Germany: €1500

  France: €1650

  Belgium: €1550

  Austria: €1450

  Ireland: €1900

  Denmark: €1750

  Sweden: €1600

  Finland: €1500

  Spain: €1250

  Portugal: €1150

  Italy: €1350

  Greece: €1000

  Poland: €1000

  Czechia: €1050

  Tasks:

  1. Calculate how many days remain until the target date  
  2. Estimate the amount the user can realistically save each month , Use average monthly expenses in {location} to estimate how much the user can realistically save per month.  
  Assume moderate spending , basically you just monthly income - average for this country = approximately how much you can save per month , but if the monthly income less then average just put 20% from monthly salary 

  3. If the goal is realistic — return that  
  4. If NOT realistic:
     - Calculate how many **days** the user will need to reach the goal at that monthly savings rate  
     - Suggest the exact **date** when the goal is realistically reachable

  ---

  Return result in strict JSON format:

  ```json
  {{
  "is_goal_realistic": true or false,
    "days_available": int,
    "estimated_monthly_savings": float,
    "required_days_to_reach_goal": int,               // only if goal is not realistic
    "recommended_completion_date": "YYYY-MM-DD"       // only if goal is not realistic
  }}
  """

  client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
  )
  completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    messages=[{"role": "system", "content": m_promt}],
    temperature=0.6,
    top_p=0.95,
    max_tokens=4096,
    frequency_penalty=0,
    presence_penalty=0,
    stream=True
  )

  # ✅ Collect the full response
  full_response = ""
  for chunk in completion:
    if chunk.choices[0].delta.content:
      full_response += chunk.choices[0].delta.content

  # ✅ Extract JSON from the response
  try:
    # Sometimes model returns a code block with ```json
    json_start = full_response.find('{')
    json_end = full_response.rfind('}') + 1
    json_text = full_response[json_start:json_end]

    result = json.loads(json_text)
    return result

  except Exception as e:
    print("❌ Failed to parse JSON:", e)
    print("🔎 Raw response:", full_response)
    return None

transaction_promt("japan", "1000", "2027-05-05", "1000")
#goal_promt(first_promt)