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


def tracking_credentials_message(report):
    return (
        "SafeSpace report received. "
        f"Case ID: {report.reference_number}. "
        f"PIN: {report.case_access_pin}. "
        "Use both to track your case status."
    )


def send_tracking_sms(report):
    phone = normalize_phone_number(report.reporter_phone)
    if not phone:
        return False, "No reporter phone number provided."

    message = tracking_credentials_message(report)
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_FROM_NUMBER")

    if twilio_sid and twilio_token and twilio_from:
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
        except requests.RequestException as exc:
            return False, f"SMS failed via Twilio: {exc}"

    sms_api_url = os.getenv("SMS_API_URL")
    sms_api_key = os.getenv("SMS_API_KEY")
    sms_sender_id = os.getenv("SMS_SENDER_ID", "SafeSpace")

    if sms_api_url and sms_api_key:
        try:
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

    return False, "SMS not configured. Set Twilio env vars or SMS_API_URL/SMS_API_KEY."
