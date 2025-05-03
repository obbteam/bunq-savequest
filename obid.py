import requests
import os
import json

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
- Also you output goes straight to my json file, so don't use ```json in the beginning and end

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

input_file = open("io_files/structured_sample_3mo.json")

data = json.dumps(json.load(input_file))

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

def transaction_promt(promt, data):
  client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
  )
  completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    messages=[{"role": "system", "content": promt + data}],
    temperature=0.6,
    top_p=0.95,
    max_tokens=4096,
    frequency_penalty=0,
    presence_penalty=0,
    stream=True
  )

  file = open('io_files/analyzed_summary.json', 'w', encoding="UTF-8")

  for chunk in completion:
    if chunk.choices[0].delta.content is not None:
      file.write(chunk.choices[0].delta.content)
      print(chunk.choices[0].delta.content, end="")
      file.flush()

  file.close()

transaction_promt(promt, data)
# goal_promt(first_promt)