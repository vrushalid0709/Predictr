import random
import time

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def otp_with_expiry():
    """Generate OTP with an expiry timestamp."""
    otp_code = generate_otp()
    expiry_time = time.time() + 300  # 5 minutes from now
    return otp_code, expiry_time
