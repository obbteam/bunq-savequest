import http.client
import json
from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import EventApiObject
from bunq import Pagination
from bunq import ApiEnvironmentType


# Create an API context for production
api_context = ApiContext.create(
    ApiEnvironmentType.SANDBOX, # SANDBOX for testing
    "sandbox_cfeb239b11862697a80e9041493acfe31e1e56eeecc42302eb44db3e",
    "risame"
)

# Save the API context to a file for future use
api_context.save("bunq_api_context.conf")

BunqContext.load_api_context(api_context)