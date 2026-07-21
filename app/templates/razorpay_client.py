import razorpay
from config import Config

client = razorpay.Client(
    auth=(
        Config.RAZORPAY_KEY_ID,
        Config.RAZORPAY_KEY_SECRET
    )
)