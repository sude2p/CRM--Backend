from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import EmailMessage
import os
import pika
from datetime import timedelta, datetime
from google.oauth2.credentials import Credentials
from django.conf import settings
from urllib.parse import urlparse
from enum import Enum
from googleapiclient.discovery import build




class SourceType(Enum):
    """
    Enumeration for different types of users in the system.

    Attributes:
        ADMIN (str): Represents a platform user, typically an administrator.
        USER (str): Represents an organizational user.
    """

    STAFF_USER = "staff_user"
    USER = "org_user"


def decode_jwt_token(token):
    """
    Decodes a JWT token to extract the user ID.

    Args:
        token (str): The JWT token to decode.

    Returns:
        int or dict: The user ID extracted from the token if valid,
                     otherwise a dictionary with an error message.
    """

    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return user_id
    except TokenError as e:
        return {"error": str(e)}


class Util:

    @staticmethod
    def send_email(data):
        """
        Sends an email using the provided data.

        Args:
            data (dict): A dictionary containing the email details. Must include:
                - 'subject' (str): The subject of the email.
                - 'body' (str): The body of the email.
                - 'to_email' (str): The recipient's email address.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_HOST_USER"),
            to=[data["to_email"]],
        )
        email.send(fail_silently=False)


# Parse the CloudAMQP URL
cloudamqp_url = os.environ.get("CLOUDAMPURL")

params = pika.URLParameters(cloudamqp_url)


def get_rabbitmq_connection():
    return pika.BlockingConnection(params)



#method for creating googlemeet link

def create_googlemeet_link(appointment_obj):
    credentials = Credentials.from_authorized_user_file(settings.GOOGLE_CREDENTIALS, settings.SCOPES)
     # Initialize the Calendar API service
    service = build('calendar', 'v3', credentials=credentials)
    # Create event start and end time based on the appointment
    start_time = datetime.combine(appointment_obj.date, appointment_obj.time)
    end_time = start_time + timedelta(minutes=60) #1 hour appointment
    event = {
        'summary': f"Appointment with {appointment_obj.contact.full_name}",
        'description': 'Online Appointment',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata', # Replace with your time zone
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata', # Replace with your time zone
        },
        'conferenceData': {
            'createRequest': {
                'requestId': '12345',
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet',
                },
            },
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'attendees': [
            {'email': 'appointment_obj.contact.email'}
            ], 
    }
    
    # Create the event with conferenceData to generate a Google Meet link
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    
     # Get the Google Meet link
     
    meet_link = created_event.get('conferenceData', {}).get('entryPoints', [])[0].get('uri')
    
    return meet_link
    
   
    
     
        
    