import json

import requests
import os

from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)


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



def goal_promt():
  with open('SavedGoal.json', 'r') as f1:
    data = json.load(f1)

  with open('events2.json', 'r') as f2:
    info = json.load(f2)
  promt = f'''
  You are an AI financial coach. Your task is to analyze a user's past 3 months of transactions and generate a JSON report with detailed savings advice, personalized challenges, and a motivation message. Your output must follow the exact JSON format described below.

  VERY IMPORTANT:
  - Your output MUST be valid JSON.
  - DO NOT include any text outside the JSON.
  - DO NOT include markdown or any explanation — ONLY the JSON block.

  ---
  USER GOAL:

  "{data["name"]}"  
  Deadline date: "{data["date"]}"
  Amount needed to save: "{data["amount"]}"
  The goal is currently **not achievable**. Your job is to help.

  ---

  YOU WILL RECEIVE:

  - A list of transactions (date, category, amount, weekday, description)

  ---

  YOUR TASKS:
  
  1. **Create a dictionary of national monthly average spending per category for the country with a country code {data["location"]}:**
    - Categories include:
         - Food
         - Transport
         - Bars / cafés
         - Entertainment
         - Shopping
         - Subscriptions
         - Rental

  2. **Analyze the user's spending behavior:**
     - Calculate/extract the total amount of income
     - Group all payment transactions by category
     - Count the number of transactions per category
     - Group by day of the week to detect repetitive spending days (e.g. always shopping on Saturdays, bars on Fridays)
     - Identify recurring behaviors or unhealthy patterns

  3. **Detect overspending:**
     - For each category:
       - Group all transaction on 6 categories: Food, Transport, Entertainment, Shopping, Rental, Subscriptions
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

  4. **Make personalized recommendations:**
     - For each overspent category, explain the issue briefly and give a short advice
     - Maximum 3 recommendations

  5. **Generate up to 3 personalized saving challenges:**
     - Each challenge must have:
       - title
       - condition (task to complete)
       - target (e.g. amount, behavior)
       - reward: XP, savings in €, or bonus (string)
       - explanation ("why this matters") — must relate to the Japan trip goal if possible

  6. **Project possible monthly savings:**
     - Based on all challenges and their savings values, estimate how much the user can save in 1 month if they succeed in all
     - Include it in a separate block called `savings_projection`

  7. **Add motivation:**
     Generate 15 short, punchy, and emotionally engaging phrases to keep a user invested in a personal saving challenge. These phrases should appear at the top of a savings app and act like dynamic micro-headlines that drive the user to continue saving money and completing daily challenges.

  Do NOT make them generic motivational quotes. Instead, make them bold, clever, and behavior-provoking — like something you'd see in a fitness app, a gamified finance app, or a startup landing page.

  Make exactly 15 phrases, not more, not less.
  Tone: bold, energetic, playful, slightly provocative (in a positive way). Each phrase should feel like a call to action or a nudge toward progress.
  Max 7 words per phrase.

  ---

  JSON OUTPUT FORMAT (strict)

  ```json
  { {
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
  }
  
  DATA:

  {info}

  '''

  client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
  )
  completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    messages=[{"role": "system", "content": promt}],
    temperature=0.6,
    top_p=0.95,
    max_tokens=4096,
    frequency_penalty=0,
    presence_penalty=0,
    stream=True
  )

  full_response = ""
  for chunk in completion:
    if chunk.choices[0].delta.content:
      print(chunk.choices[0].delta.content, end="")
      full_response += chunk.choices[0].delta.content

  try:
    # Extract JSON block
    import re

    # Extract JSON block (try to remove markdown, extra text)
    json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
    if not json_match:
      raise ValueError("❌ No JSON object found in response.")

    json_text = json_match.group()

    # Remove any `// comments`
    json_text = re.sub(r'//.*', '', json_text)
    json_text = json_text.strip()

    result = json.loads(json_text)

    with open('analyzed_summary.json', 'w') as f:
      json.dump(result, f)
    json.dumps(result)
    return result


  except Exception as e:
    print("❌ Failed to parse JSON:", e)
    print("🔎 Raw response:", full_response)
    return None

def transaction_promt(goal_name, amount, due_date, income):
  location = "Netherlands"
  goal_data = {"name": goal_name, "amount": amount, "date": due_date, "location":location}
  print(due_date)
  goal_data.update({"location": "NL"})
  with open('SavedGoal.json', 'w') as f:
    json.dump(goal_data, f)


  m_promt = f"""

  today is 2025-05-02 (format: YYYY-MM-DD)
  You are an AI financial coach
  
    VERY IMPORTANT:
  - Your output MUST be valid JSON.
  - DO NOT include any text outside the JSON.
  - DO NOT include markdown or any explanation — ONLY the JSON block.


  The user has the following information:
  - Goal: "{goal_name}" 
  - Amount: {amount}€
  - Target date: {due_date}
  - Country: {location}
  - Monthly income: {income}€



  Tasks:

  1. Calculate how many days remain until the target date  
  2. Estimate the amount the user can realistically save each month, take the average of the amount a regular person spends a month in {location} and subtract it from the income of this particular person. If

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

  try:
    import re

    # Extract strict JSON block using regex
    match = re.search(r'\{[\s\S]*?\}', full_response)
    if not match:
      raise ValueError("No JSON object found.")

    json_text = match.group()

    # Clean any invalid inline comments (e.g. //...)
    json_text = re.sub(r'//.*', '', json_text)
    json_text = json_text.strip()

    result = json.loads(json_text)
    return result


  except Exception as e:
    print("❌ Failed to parse JSON:", e)
    print("🔎 Raw response:", full_response)
    return None

