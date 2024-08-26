from gmailclient import GmailClient
from gmail_structures import Thread, Message


class ThreadClient(GmailClient):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.threads = {}  # Store the thread_id : Thread

    # Todo this need to be checked
    def fetch_threads(self, user_id, maximum_threads=-1):
        """Retrieve a list of threads."""
        count = 100
        fetched_mails = 0
        page_token = None

        while True:
            if maximum_threads != -1 and fetched_mails + count > maximum_threads:
                count = maximum_threads - fetched_mails

            response = self.service.users().threads().list(userId=user_id, maxResults=count,
                                                           pageToken=page_token).execute()
            threads = response.get('threads', [])

            for thread in threads:
                self.threads[thread['id']] = Thread(thread_id=thread['id'], history_id=thread['historyId'],
                                                    messages=[])

            fetched_mails += len(threads)

            page_token = response.get('nextPageToken')
            if not page_token or (maximum_threads != -1 and fetched_mails >= maximum_threads):
                break

    # Todo this need to be checked
    def fetch_thread_messages(self, user_id, thread_id):
        """Retrieve all messages within a thread."""
        thread_data = self.service.users().threads().get(userId=user_id, id=thread_id).execute()
        message = thread_data.get('messages', [])
        return message

    def fetch_all_messages_from_threads(self, user_id, maximum_threads=-1):
        """Retrieve and print all messages from threads."""
        self.fetch_threads(user_id, maximum_threads)

        if not self.threads:
            print("No threads found.")
            return

        for thread_id in self.threads:

            history_id = self.threads[thread_id].history_id
            messages = self.fetch_thread_messages(user_id, thread_id)

            for message in messages:
                msg_id = message['id']
                full_message = self.get_full_message(user_id, msg_id)
                subject, from_email, date, cc, bcc = GmailClient.extract_message_headers(full_message)
                body = GmailClient.get_message_body(full_message)

                # Create a Message object and append it to the Thread
                message_obj = Message(from_email=from_email, subject=subject, date=date, cc=cc, bcc=bcc, body=body)
                self.threads[thread_id].messages.append(message_obj)

    def print_threads_messages(self):
        """Print all messages from all threads."""
        if not self.threads:
            print("No threads available to display.")
            return

        for thread_id, thread in self.threads.items():
            print(f"Thread ID: {thread_id}")
            print(f"History ID: {thread.history_id}")
            print("Messages:")
            for message in thread.messages:
                GmailClient.print_message_details(message)
            print("=" * 70)  # Separator between threads for clarity
