from typing import List

from googleapiclient.discovery import build
import base64
from gmail_structures import Thread, Message



class GmailClient:
    def __init__(self, credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    def get_full_message(self, user_id, msg_id):
        """Retrieve the full message content for a given message ID."""
        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        return message

    @staticmethod
    def extract_message_headers(message):
        """Extract relevant headers from a message."""
        headers = message['payload']['headers']
        subject = ""
        from_email = ""
        date = ""
        cc = ""
        bcc = ""

        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                from_email = header['value']
            elif header['name'] == 'Date':
                date = header['value']
            elif header['name'] == 'Cc':
                cc = header['value']
            elif header['name'] == 'Bcc':
                bcc = header['value']

        return subject, from_email, date, cc, bcc

    @staticmethod
    def get_message_body(message):
        """Decode the message body."""
        payload = message['payload']
        body = ""

        if 'parts' in payload:
            # Multipart email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body_data = part['body']['data']
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            # Single part email
            body_data = payload['body']['data']
            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            body = "No body content found."

        return body

    @staticmethod
    def print_message_details(message: Message):
        """Print the message details systematically."""
        print(f"  From: {message.from_email}")
        print(f"  Subject: {message.subject}")
        print(f"  Date: {message.date}")
        print(f"  Cc: {message.cc}")
        print(f"  Bcc: {message.bcc}")
        print(f"  Full Message:\n{message.body}")
        print("-" * 50)  # Separator for readability



