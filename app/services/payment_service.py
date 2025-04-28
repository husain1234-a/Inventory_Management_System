import stripe
from app.core.config import settings
from fastapi import HTTPException

stripe.api_key = settings.STRIPE_API_KEY

class PaymentService:
    async def process_payment(self, transaction_id: int, amount: float):
        try:
            # Create a payment intent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                metadata={"transaction_id": transaction_id}
            )
            return intent
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def verify_webhook(self, payload: dict) -> dict:
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload,
                stripe.api_key,
                settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Extract relevant information
            if event.type == "payment_intent.succeeded":
                payment_intent = event.data.object
                return {
                    "transaction_id": payment_intent.metadata.transaction_id,
                    "status": "completed",
                    "payment_id": payment_intent.id
                }
            elif event.type == "payment_intent.payment_failed":
                payment_intent = event.data.object
                return {
                    "transaction_id": payment_intent.metadata.transaction_id,
                    "status": "failed",
                    "payment_id": payment_intent.id
                }
            
            return None
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))