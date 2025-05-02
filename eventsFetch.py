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

# Create pagination
pagination = Pagination()
pagination.count = 10

# List payments
events = EventApiObject.list(params=pagination.url_params_count_only).value

# Display payments
for event in events:
    print(event.id_)
    print(event.object_.RequestInquiry.amount_responded.value)
    print(event.object_.RequestInquiry.description) 
    print(event.__dict__) #additional_transaction_information NOT WORKING
    