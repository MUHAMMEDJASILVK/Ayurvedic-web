import logging
import urllib.request
import urllib.parse
import json
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

logger = logging.getLogger('accounts')

def send_registration_email_otp(user, email_otp):
    """
    Sends the 6-digit verification OTP to the user's registered email address.
    Never exposes the OTP on the webpage.
    """
    subject = f"Your Verification OTP for Kerala Ayurveda Portal: {email_otp}"
    recipient_email = user.email
    user_name = user.get_full_name() or user.username or "Customer"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f3eb; margin: 0; padding: 20px; color: #1e3a1e; }}
        .email-container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e2d9cc; }}
        .email-header {{ background: linear-gradient(135deg, #1b5e20, #2e7d32); color: #ffffff; padding: 30px 20px; text-align: center; }}
        .email-header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; }}
        .email-header p {{ margin: 6px 0 0; font-size: 14px; opacity: 0.9; color: #e8f5e9; }}
        .email-body {{ padding: 30px; }}
        .greeting {{ font-size: 16px; margin-bottom: 16px; }}
        .otp-box {{ background: #f0fdf4; border: 2px dashed #16a34a; border-radius: 10px; padding: 20px; text-align: center; margin: 25px 0; }}
        .otp-label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; color: #15803d; font-weight: 700; margin-bottom: 8px; }}
        .otp-code {{ font-size: 38px; font-weight: 800; letter-spacing: 8px; color: #14532d; font-family: 'Courier New', Courier, monospace; }}
        .notice {{ font-size: 13px; color: #6b7280; line-height: 1.6; margin-top: 20px; }}
        .security-tip {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px; margin-top: 20px; font-size: 13px; color: #92400e; }}
        .email-footer {{ background: #faf8f5; padding: 20px; text-align: center; font-size: 12px; color: #8c8273; border-top: 1px solid #f0e8dc; }}
      </style>
    </head>
    <body>
      <div class="email-container">
        <div class="email-header">
          <h1>🌿 Kerala Ayurveda Store</h1>
          <p>Authentic Traditional Ayurvedic Formulations</p>
        </div>
        <div class="email-body">
          <p class="greeting">Namaste <strong>{user_name}</strong>,</p>
          <p>Thank you for registering with Kerala Ayurveda Store. To ensure the security of your account and verify your email address, please enter the following One-Time Password (OTP):</p>
          
          <div class="otp-box">
            <div class="otp-label">Your Email Verification Code</div>
            <div class="otp-code">{email_otp}</div>
          </div>
          
          <p class="notice">
            ⏳ This code is valid for <strong>10 minutes</strong>. Do NOT share this code with anyone, including Kerala Ayurveda staff.
          </p>

          <div class="security-tip">
            <strong>Security Tip:</strong> If you did not initiate this registration, please disregard this email. No account will be activated without this OTP.
          </div>
        </div>
        <div class="email-footer">
          &copy; 2026 Kerala Ayurveda Store &bull; Kottakkal, Thrissur & Aluva Traditions &bull; All Rights Reserved.
        </div>
      </div>
    </body>
    </html>
    """

    plain_message = f"""
Namaste {user_name},

Thank you for registering with Kerala Ayurveda Store.
Your Email Verification OTP is: {email_otp}

This code is valid for 10 minutes.
Do not share this code with anyone.

Kerala Ayurveda Store
Authentic Traditional Ayurvedic Formulations
    """

    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', 'keralaayurvedastore@gmail.com')
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"\n[EMAIL DISPATCH] Sent Email OTP to {recipient_email} successfully.\n")
        return True, None
    except Exception as e:
        error_msg = str(e)
        print(f"\n[EMAIL DISPATCH FAILED / DEV NOTICE]")
        print(f"Could not send email via SMTP to {recipient_email}. Reason: {error_msg}")
        print(f">> DEV CONSOLE BACKUP: Email OTP for {recipient_email} is [{email_otp}] <<\n")
        logger.error(f"Failed to send email OTP: {e}")
        return False, error_msg


def send_registration_sms_otp(user, phone_otp):
    """
    Sends the 6-digit verification OTP to the user's registered mobile phone.
    Supports Fast2SMS or custom SMS Gateway via settings.SMS_API_KEY.
    """
    phone = user.phone_number
    sms_text = f"Your Kerala Ayurveda verification OTP is {phone_otp}. Valid for 10 mins. Do not share with anyone."
    sms_api_key = getattr(settings, 'SMS_API_KEY', '')

    if sms_api_key:
        try:
            # Example Fast2SMS Quick SMS API integration
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                'authorization': sms_api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = urllib.parse.urlencode({
                'variables_values': phone_otp,
                'route': 'otp',
                'numbers': phone,
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=8) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                print(f"[SMS DISPATCH] Sent SMS OTP to {phone}: {resp_data}")
                return True, None
        except Exception as e:
            print(f"[SMS DISPATCH FAILED] Error sending SMS via gateway: {e}")
            logger.error(f"SMS Gateway error: {e}")
            return False, str(e)
    else:
        # Development mode when no SMS API key is configured yet
        print(f"\n[SMS DISPATCH - CONSOLE/DEV LOG]")
        print(f">> Outgoing SMS to {phone}: \"{sms_text}\" <<")
        print(f">> Phone OTP is [{phone_otp}] (Valid for 10 min) <<\n")
        return True, "Dev Mode: Logged to terminal"
