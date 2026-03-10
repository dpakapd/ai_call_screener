import os
from datetime import datetime, timedelta, timezone
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Setup Twilio Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# Calculate the cutoff (10 days ago)
cutoff_date = datetime.now(timezone.utc) - timedelta(days=10)

print(f"--- Starting Cleanup: {datetime.now()} ---")

# Pull the list of recordings created before the cutoff
recordings = client.recordings.list(date_created_before=cutoff_date)

if not recordings:
    print("No old recordings found.")
else:
    for record in recordings:
        print(f"Deleting recording SID: {record.sid} (Created: {record.date_created})")
        client.recordings(record.sid).delete()

print("--- Cleanup Complete ---")