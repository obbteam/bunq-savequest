from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import (MonetaryAccountSavingsApiObject, PaymentApiObject)
from bunq.sdk.model.generated.object_ import AmountObject, PointerObject

api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)


def create_savings_account(currency, description, goal_amount):
    """
    Creates MonetaryAccountSavings and returns (savings_id, savings_iban).
    """
    response = MonetaryAccountSavingsApiObject.create(
        currency=currency,
        description=description,
        savings_goal={"value": f"{goal_amount}", "currency": currency},
    )
    savings_id = response.value
    print(savings_id)

    # fetch the account so we can read its IBAN
    aliases = MonetaryAccountSavingsApiObject.get(savings_id).value.alias
    iban = ""
    for alias in aliases:
        if alias.type_ == "IBAN":
            iban = alias.value
            break
    return iban


def get_primary_monetary_account_id():
    """
    Returns the first ACTIVE monetary‑account id of the logged‑in user.
    """
    iban = ""
    aliases = BunqContext.user_context().primary_monetary_account.alias
    for alias in aliases:
        if alias.type_ == "IBAN":
            iban = alias.value
            break
    return iban


def transfer_to_savings(src_id, dst_iban, amount, currency):
    return PaymentApiObject.create(
        AmountObject(amount, currency),
        PointerObject("IBAN", dst_iban),
        "Top‑up savings",
        monetary_account_id=src_id,
    ).value

def cur_saving_acc_balance (acc_id):
    acc = MonetaryAccountSavingsApiObject.get(acc_id).value.balance
    return {acc.value, acc.currency}


get_primary_monetary_account_id()
# create_savings_account("EUR", "Japan trip 1000", 1000.0)
cur_saving_acc_balance(2114467)
