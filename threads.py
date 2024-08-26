from typing import List

from googleapiclient.discovery import build
from OAuth import authentication
import base64
from gmail_structures import Thread, Message

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailClient:
    def __init__(self, credentials):
        self.service = build("gmail", "v1", credentials=credentials)
        self.threads = {}  # Store the thread_id : Thread

    # Todo this need to be checked
    def fetch_threads(self, user_id, maximum_mails=-1):
        """Retrieve a list of threads."""
        count = 100
        fetched_mails = 0
        page_token = None

        while True:
            if maximum_mails != -1 and fetched_mails + count > maximum_mails:
                count = maximum_mails - fetched_mails

            response = self.service.users().threads().list(userId=user_id, maxResults=count,
                                                           pageToken=page_token).execute()
            threads = response.get('threads', [])

            for thread in threads:
                self.threads[thread['id']] = Thread(thread_id=thread['id'], history_id=thread['historyId'], messages=[])

            fetched_mails += len(threads)

            page_token = response.get('nextPageToken')
            if not page_token or (maximum_mails != -1 and fetched_mails >= maximum_mails):
                break

    # Todo this need to be checked
    def fetch_thread_messages(self, user_id, thread_id, history_id=None):
        """Retrieve all messages within a thread."""
        thread_data = None
        if history_id and history_id > self.threads[thread_id].history_id:
            thread_data = self.service.users().messages().get(userId=user_id,
                                                              id=thread_id, q='after:' + history_id).execute()
        else:
            thread_data = self.service.users().messages().get(userId=user_id, id=thread_id).execute()
        return thread_data['messages']

    def get_full_message(self, user_id, msg_id):
        """Retrieve the full message content for a given message ID."""
        message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        return message

    def extract_message_headers(self, message):
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

    def get_message_body(self, message):
        """Decode the message body."""
        if 'data' in message['payload']['parts'][0]['body']:
            body_data = message['payload']['parts'][0]['body']['data']
            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            body = "No body content found."
        return body

    def print_message_details(self, message: Message):
        """Print the message details systematically."""
        print(f"  From: {message.from_email}")
        print(f"  Subject: {message.subject}")
        print(f"  Date: {message.date}")
        print(f"  Cc: {message.cc}")
        print(f"  Bcc: {message.bcc}")
        print(f"  Full Message:\n{message.body}")
        print("-" * 50)  # Separator for readability

    def fetch_all_messages_from_threads(self, user_id):
        """Retrieve and print all messages from threads."""
        self.fetch_threads(user_id)

        if not self.threads:
            print("No threads found.")
            return

        for thread in self.threads:
            thread_id = thread['id']
            history_id = thread['historyId']
            messages = self.fetch_thread_messages(user_id, thread_id)

            thread_data = Thread(thread_id=thread_id, history_id=history_id, messages=[])

            for message in messages:
                msg_id = message['id']
                full_message = self.get_full_message(user_id, msg_id)
                subject, from_email, date, cc, bcc = self.extract_message_headers(full_message)
                body = self.get_message_body(full_message)

                # Create a Message object and append it to the Thread
                message_obj = Message(from_email=from_email, subject=subject, date=date, cc=cc, bcc=bcc, body=body)
                thread_data.messages.append(message_obj)

            self.threads.append(thread_data)


if __name__ == "__main__":
    creds = authentication(SCOPES)
    gmail_client = GmailClient(creds)

    # Call the function to get all messages from threads
    # gmail_client.get_all_messages_from_threads("me")

