from flask import Flask, request, jsonify
import stripe
import os

app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Map product SKUs to Stripe Price IDs
PRICE_MAP = {
    "starter": "price_123_starter",    # replace with actual Stripe price ID
    "pro": "price_456_pro",            # replace with actual Stripe price ID
    "premium": "price_789_premium"     # replace with actual Stripe price ID
}

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    product_key = data.get("product")

    if product_key not in PRICE_MAP:
        return jsonify({"error": "Invalid product."}), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": PRICE_MAP[product_key],
                "quantity": 1,
            }],
            subscription_data={
                "trial_period_days": 30
            },
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel"
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    # Handle successful subscription
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Subscription started:", session["id"])

        # TODO: Fire webhook to GHL or Make.com here

    return jsonify(success=True)
