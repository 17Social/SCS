from flask import Flask, request, jsonify
import stripe
import os

app = Flask(__name__)

# ✅ Set your secret key from Railway environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ✅ This is the correct endpoint your frontend and Bolt are calling
@app.route("/api/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json()
    price_id = data.get("priceId")

    if not price_id:
        return jsonify({"error": "Missing priceId"}), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url="https://17social.net/success",
            cancel_url="https://17social.net/cancel"
        )
        return jsonify({ "id": session.id })  # ✅ This is what your frontend expects
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

# Optional: Stripe webhook for post-payment logic
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
        print("✅ Payment complete — Session ID:", session["id"])
        # TODO: You can fire webhook to GHL or internal logic here

    return jsonify(success=True)

# ✅ Required for Railway to expose on port 8080
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
