import http.client
import json
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import EventApiObject
from bunq.sdk.model.generated.endpoint import PaymentApiObject
from bunq import Pagination
from bunq import ApiEnvironmentType

api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)

conn = http.client.HTTPSConnection("public-api.sandbox.bunq.com")
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

if "Response" in response:
    for event in response["Response"]:
 
        print(f"Event ID: {event['Event']['id']}")
        print(f"Created: {event['Event']['created']}")
        print(f"Status: {event['Event']['status']}")
        print(f"Action: {event['Event']['action']}")

        if 'object' in event['Event']:
            event_object = event['Event']['object']
            if 'RequestInquiry' in event_object:
                request_inquiry = event_object['RequestInquiry']
                print(f"Request Inquiry ID: {request_inquiry['id']}")
                print(f"Amount Inquired: {request_inquiry['amount_inquired']['value']} {request_inquiry['amount_inquired']['currency']}")
                print(f"Amount Responded: {request_inquiry['amount_responded']['value']} {request_inquiry['amount_responded']['currency']}")
                print(f"Time Responded: {request_inquiry['time_responded']}")
            else:
                print("No RequestInquiry details available.")
            if 'additional_transaction_information' in event['Event']:
                additionalInfo = event['Event']['additional_transaction_information']
                print(f"category: {additionalInfo['category']['category']}")
                print(f"type: {additionalInfo['category']['type']}")
            else:
                print("No additional info details available.")
        print("\n---\n")
else:
    print("No events found.")