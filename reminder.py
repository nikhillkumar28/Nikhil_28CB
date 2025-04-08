import json
import time
from datetime import datetime
from plyer import notification

EVENTS_FILE = "pet_care_events.json"

def check_reminders():
    """Check for upcoming events and send notifications."""
    while True:
        try:
            with open(EVENTS_FILE, "r") as file:
                events = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            events = []

        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        for event in events:
            if event["event_time"] <= current_time:
                notification.notify(
                    title="Pet Care Reminder",
                    message=f"Reminder: {event['event_name']} is scheduled now!",
                    timeout=10
                )

                # Remove the event after notifying
                events.remove(event)

                with open(EVENTS_FILE, "w") as file:
                    json.dump(events, file, indent=4)

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    check_reminders()
