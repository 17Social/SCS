from flask import Flask, request, jsonify
from flask_cors import CORS
import stripe
import os

app = Flask(__name__)

# ✅ CORS FIX: Allow frontend to talk to backend securely
# TEMP: allow all during testing
CORS(app)

# 🔒 Later, restrict to only your frontend domains like this:
# CORS(app, resources={r"/api/*": {"origins": [
#     "https://yourdomain.com",
#     "https://yourboltproject.bolt.fun"
# ]}})

# ✅ Stripe secret key from .env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ✅ Price IDs — install + monthly per tier
PRICE_MAP = {
    "starter": {
        "install": "price_1RsoObLzByxOBy7vZ7iAvQbw",
        "monthly": "price_1RsuNNLzByxOBy7vZ4D6nL2F"
    },
    "growth": {
        "install": "price_1RsoOcLzByxOBy7vrDsK4wH9",
        "monthly": "price_1RsuNvLzByxOBy7v0NToM3S3"
    },
    "premium": {
        "install": "price_1RsoOdLzByxOBy7vxpHt9FIx",
        "monthly": "price_1RsuOALzByxOBy7v2pjtrd1D"
    }
}

# ✅ API endpoint for Stripe Checkout
@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    product = data.get("product")

    if product not in PRICE_MAP:
        return jsonify({"error": "Invalid product tier."}), 400

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": PRICE_MAP[product]["install"],
                    "quantity": 1,
                },
                {
                    "price": PRICE_MAP[product]["monthly"],
                    "quantity": 1,
                }
            ],
            subscription_data={
                "trial_period_days": 30
            },
            success_url="https://17social.net/success",
            cancel_url="https://17social.net/cancel"
        )
        return jsonify({ "id": session.id })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

# ✅ Optional webhook for post-checkout actions
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Stripe Checkout Complete — Session ID:", session["id"])
        # TODO: Call Make.com or trigger onboarding flow

    return jsonify(success=True)

# ✅ For Railway container to run correctly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

