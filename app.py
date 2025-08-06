import os
import stripe
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down to your Bolt domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe price mappings
SETUP_FEES = {
    "starter": "price_1RsncmByxOBy7v4JrGXvUhw6",
    "growth":  "price_1RsncOByxOBy7v4JnTkAaXXz",
    "pro":     "price_1RsncVByxOBy7v4J6e1NStv9",
}

MONTHLY_FEES = {
    "starter": "price_1RsncmByxOBy7v4JqGulD1bL",  # $400/mo after 30 days
    "growth":  "price_1RsoOdLzByxOBy7v4JtSjrqN",  # $1000/mo after 30 days
    "pro":     "price_1RsncYByxOBy7v4JdnyXYcXY",  # $600/mo after 30 days
}

class CheckoutSessionRequest(BaseModel):
    tier: str  # starter, growth, pro
    email: str

@app.post("/api/create-checkout-session")
async def create_checkout_session(req: CheckoutSessionRequest):
    try:
        tier = req.tier.lower()
        customer_email = req.email

        if tier not in SETUP_FEES or tier not in MONTHLY_FEES:
            return {"error": "Invalid tier selected."}

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=customer_email,
            line_items=[
                {
                    "price": SETUP_FEES[tier],
                    "quantity": 1,
                },
                {
                    "price": MONTHLY_FEES[tier],
                    "quantity": 1,
                },
            ],
            subscription_data={
                "trial_period_days": 30,
            },
            success_url="https://17social.net/checkout-success",
            cancel_url="https://17social.net/checkout-cancelled",
        )
        return {"sessionId": session.id}

    except Exception as e:
        return {"error": str(e)}

