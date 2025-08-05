import stripe
import json
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # set this in Railway

# Product definitions
products = [
    {
        "name": "Starter Install (One-Time)",
        "type": "one_time",
        "amount": 500000  # $5,000 in cents
    },
    {
        "name": "Starter Subscription",
        "type": "recurring",
        "amount": 40000,  # $400/month
        "trial_days": 30
    },
    {
        "name": "Growth Install (One-Time)",
        "type": "one_time",
        "amount": 1500000  # $15,000
    },
    {
        "name": "Growth Subscription",
        "type": "recurring",
        "amount": 60000,
        "trial_days": 30
    },
    {
        "name": "Premium Install (One-Time)",
        "type": "one_time",
        "amount": 2500000  # $25,000
    },
    {
        "name": "Premium Subscription",
        "type": "recurring",
        "amount": 100000,
        "trial_days": 30
    }
]

# Output dictionary
price_ids = {}

for product in products:
    created_product = stripe.Product.create(name=product["name"])

    if product["type"] == "one_time":
        price = stripe.Price.create(
            unit_amount=product["amount"],
            currency="usd",
            product=created_product.id
        )
    else:
        price = stripe.Price.create(
            unit_amount=product["amount"],
            currency="usd",
            recurring={"interval": "month", "trial_period_days": product["trial_days"]},
            product=created_product.id
        )

    price_ids[product["name"]] = price.id
    print(f"{product['name']} → {price.id}")

# Save price IDs to file
with open("price_ids.json", "w") as f:
    json.dump(price_ids, f, indent=2)
