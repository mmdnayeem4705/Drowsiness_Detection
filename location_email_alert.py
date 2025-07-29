import requests
import smtplib
from email.mime.text import MIMEText

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data['loc']  # Format: "latitude,longitude"
        city = data.get('city', 'Unknown City')
        region = data.get('region', 'Unknown Region')
        country = data.get('country', 'Unknown Country')
        return location, city, region, country
    except:
        return None, None, None, None

def send_location_email(receiver_email):
    loc, city, region, country = get_location()
    if loc:
        subject = "🚨 Emergency Alert: Driver Drowsiness Detected"
        body = f"""
        ⚠️ Emergency Detected!

        The driver has failed to respond to repeated alerts.

        Approximate Location:
        City: {city}
        Region: {region}
        Country: {country}
        Google Maps: https://www.google.com/maps?q={loc}

        Please take necessary action immediately.
        """

        # Setup email
        sender_email = "mmdnayeem4705@gmail.com"
        sender_password = "mmn@2003"  # Use App Password (not real Gmail password)
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print("🚀 Emergency email sent successfully.")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    else:
        print("❌ Could not fetch location.")

# Example call (trigger this after 4th alert)
# send_location_email("familymember@example.com")
