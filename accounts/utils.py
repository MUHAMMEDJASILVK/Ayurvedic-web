import logging
import urllib.request
import urllib.parse
import json
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger('accounts')

def send_registration_email_otp(user, email_otp, phone_otp=None):
    """
    Sends the 6-digit verification OTP to the user's registered email address.
    Also includes the Mobile verification code as backup if SMS gateway is delayed.
    NEVER exposes the OTP on the webpage.
    """
    subject = f"Your Verification Codes for Kerala Ayurveda Store"
    recipient_email = user.email
    user_name = user.get_full_name() or user.username or "Customer"

    phone_section_html = ""
    phone_section_plain = ""
    if phone_otp:
        phone_section_html = f"""
          <div class="otp-box" style="background: #eff6ff; border: 2px dashed #3b82f6; margin-top: 20px;">
            <div class="otp-label" style="color: #1d4ed8;">Your Mobile Verification Code</div>
            <div class="otp-code" style="color: #1e40af;">{phone_otp}</div>
            <div style="font-size: 11px; color: #475569; margin-top: 6px;">
              Registered Mobile: +91 {user.phone_number}
            </div>
          </div>
        """
        phone_section_plain = f"\nYour Mobile Verification OTP is: {phone_otp}\n(For phone +91 {user.phone_number})\n"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f3eb; margin: 0; padding: 20px; color: #1e3a1e; }}
        .email-container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e2d9cc; }}
        .email-header {{ background: linear-gradient(135deg, #1b5e20, #2e7d32); color: #ffffff; padding: 26px 20px; text-align: center; }}
        .email-header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
        .email-header p {{ margin: 6px 0 0; font-size: 13px; color: #e8f5e9; }}
        .email-body {{ padding: 28px 30px; }}
        .greeting {{ font-size: 15px; margin-bottom: 14px; }}
        .otp-box {{ background: #f0fdf4; border: 2px dashed #16a34a; border-radius: 10px; padding: 18px; text-align: center; margin: 20px 0; }}
        .otp-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #15803d; font-weight: 700; margin-bottom: 6px; }}
        .otp-code {{ font-size: 36px; font-weight: 800; letter-spacing: 6px; color: #14532d; font-family: 'Courier New', Courier, monospace; }}
        .notice {{ font-size: 12px; color: #6b7280; line-height: 1.5; margin-top: 18px; }}
        .security-tip {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 10px 14px; margin-top: 18px; font-size: 12px; color: #92400e; }}
        .email-footer {{ background: #faf8f5; padding: 16px; text-align: center; font-size: 12px; color: #8c8273; border-top: 1px solid #f0e8dc; }}
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
          <p>Thank you for registering. To ensure account security and verify your credentials, please use the verification codes below to complete your registration:</p>
          
          <div class="otp-box">
            <div class="otp-label">Your Email Verification Code</div>
            <div class="otp-code">{email_otp}</div>
            <div style="font-size: 11px; color: #475569; margin-top: 6px;">
              Registered Email: {recipient_email}
            </div>
          </div>

          {phone_section_html}
          
          <p class="notice">
            ⏳ These codes are valid for <strong>10 minutes</strong>. Do NOT share these codes with anyone.
          </p>

          <div class="security-tip">
            <strong>Security Notice:</strong> If you did not initiate this request, please disregard this email. No account will be activated without entering these codes.
          </div>
        </div>
        <div class="email-footer">
          &copy; 2026 Kerala Ayurveda Store &bull; All Rights Reserved.
        </div>
      </div>
    </body>
    </html>
    """

    plain_message = f"""
Namaste {user_name},

Thank you for registering with Kerala Ayurveda Store.
Your Email Verification OTP is: {email_otp}
{phone_section_plain}
These codes are valid for 10 minutes.
Do not share these codes with anyone.

Kerala Ayurveda Store
    """

    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '') or 'keralaayurvedastore@gmail.com'
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=sender,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"\n[EMAIL DISPATCH SUCCESS] Real email sent to {recipient_email} using {sender}\n")
        return True, None
    except Exception as e:
        error_msg = str(e)
        print(f"\n[EMAIL DISPATCH FAILED] Could not send via SMTP to {recipient_email}: {error_msg}\n")
        logger.error(f"Failed to send email OTP: {e}")
        return False, error_msg


def send_registration_sms_otp(user, phone_otp):
    """
    Sends the 6-digit verification OTP to the user's registered mobile phone.
    Supports Fast2SMS or custom SMS Gateway via settings.SMS_API_KEY.
    """
    phone = user.phone_number
    sms_text = f"Your Kerala Ayurveda verification OTP is {phone_otp}. Valid for 10 mins. Do not share with anyone."
    sms_api_key = getattr(settings, 'SMS_API_KEY', '').strip()

    if sms_api_key and sms_api_key != 'your_fast2sms_api_key_here':
        try:
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
                print(f"[SMS DISPATCH SUCCESS] Sent SMS OTP to {phone}: {resp_data}")
                return True, None
        except Exception as e:
            print(f"[SMS DISPATCH FAILED] Error sending SMS via gateway: {e}")
            logger.error(f"SMS Gateway error: {e}")
            return False, str(e)
    else:
        print(f"\n[SMS DISPATCH - LOG] Outgoing SMS to {phone}: {phone_otp}\n")
        return True, "SMS logged"
