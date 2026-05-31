import os
import re
import requests


def normalize_phone_number(phone):
    cleaned = re.sub(r"[\s\-()]", "", phone or "")
    if cleaned.startswith("+"):
        return cleaned
    if cleaned.startswith("0") and len(cleaned) >= 10:
        return "+254" + cleaned[1:]
    if cleaned.startswith("254"):
        return "+" + cleaned
    return cleaned


def normalize_twilio_number(phone):
    cleaned = re.sub(r"[\s\-()]", "", phone or "")
    if cleaned.startswith("+"):
        return cleaned
    if cleaned.startswith("0") and len(cleaned) >= 10:
        return "+254" + cleaned[1:]
    if cleaned.startswith("254"):
        return "+" + cleaned
    return cleaned


def tracking_credentials_message(report):
    return (
        "SafeSpace report received. "
        f"Case ID: {report.reference_number}. "
        f"PIN: {report.case_access_pin}. "
        "Use both to track your case status."
    )


def send_tracking_sms(report):
    try:
        phone = normalize_phone_number(report.reporter_phone)
        if not phone:
            return False, "No reporter phone number provided."

        message = tracking_credentials_message(report)
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_from = normalize_twilio_number(
            os.getenv("TWILIO_FROM_NUMBER")
            or os.getenv("TWILIO_FROM")
            or os.getenv("TWILIO_PHONE_NUMBER")
        )

        if twilio_sid or twilio_token or twilio_from:
            missing_twilio = [
                name for name, value in [
                    ("TWILIO_ACCOUNT_SID", twilio_sid),
                    ("TWILIO_AUTH_TOKEN", twilio_token),
                    ("TWILIO_FROM_NUMBER or TWILIO_FROM or TWILIO_PHONE_NUMBER", twilio_from),
                ]
                if not value
            ]
            if missing_twilio:
                return False, (
                    "Twilio SMS configuration incomplete. "
                    f"Missing: {', '.join(missing_twilio)}. "
                    "Set all required Twilio vars or use SMS_API_URL/SMS_API_KEY instead."
                )

            endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            try:
                response = requests.post(
                    endpoint,
                    data={"From": twilio_from, "To": phone, "Body": message},
                    auth=(twilio_sid, twilio_token),
                    timeout=20,
                )
                response.raise_for_status()
                return True, "Tracking credentials SMS sent via Twilio."
            except requests.HTTPError as exc:
                try:
                    error_body = response.json()
                    error_message = error_body.get("message") or error_body.get("error_message")
                    error_code = error_body.get("code")
                    if error_message:
                        return False, f"SMS failed via Twilio: {error_message} (code {error_code})"
                except ValueError:
                    pass
                return False, f"SMS failed via Twilio: {exc}"
            except requests.RequestException as exc:
                return False, f"SMS failed via Twilio: {exc}"

        sms_api_url = os.getenv("SMS_API_URL")
        sms_api_key = os.getenv("SMS_API_KEY")
        sms_api_username = os.getenv("SMS_API_USERNAME")
        sms_sender_id = os.getenv("SMS_SENDER_ID", "SafeSpace")

        if sms_api_url or sms_api_key:
            missing_custom = [
                name for name, value in [
                    ("SMS_API_URL", sms_api_url),
                    ("SMS_API_KEY", sms_api_key),
                ]
                if not value
            ]
            if missing_custom:
                return False, (
                    "Custom SMS provider configuration incomplete. "
                    f"Missing: {', '.join(missing_custom)}. "
                    "Set both SMS_API_URL and SMS_API_KEY to enable this path."
                )

            try:
                if sms_api_url and "africastalking.com" in sms_api_url:
                    # Africa's Talking requires API key in the apiKey header and form-encoded body.
                    sms_api_username = sms_api_username or os.getenv("AFRICASTALKING_USERNAME") or "sandbox"
                    response = requests.post(
                        sms_api_url,
                        data={
                            "username": sms_api_username,
                            "to": phone,
                            "message": message,
                            "from": sms_sender_id,
                        },
                        headers={
                            "apiKey": sms_api_key,
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        timeout=20,
                    )
                else:
                    response = requests.post(
                        sms_api_url,
                        json={
                            "to": phone,
                            "message": message,
                            "from": sms_sender_id,
                        },
                        headers={"Authorization": f"Bearer {sms_api_key}"},
                        timeout=20,
                    )

                response.raise_for_status()
                return True, "Tracking credentials SMS sent."
            except requests.RequestException as exc:
                return False, f"SMS failed: {exc}"

        # Development fallback: log SMS to console when no provider is configured
        import sys
        print("\n" + "="*60, file=sys.stderr)
        print("📱 SMS SENT (Development Mode):", file=sys.stderr)
        print(f"   To: {phone}", file=sys.stderr)
        print(f"   Message: {message}", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        return True, "SMS logged to console (development mode - no provider configured)."
    
    except Exception as e:
        # Catch-all for any unexpected errors
        import traceback
        traceback.print_exc()
        return False, f"Unexpected SMS error: {str(e)}"
