from gmailclient import GmailClient

class MailClient(GmailClient):
    def __init__(self, credentials):
        super().__init__(credentials)
        self.mails = {}

    def fetch_all_messages(self, user_id='me', maximum_messages=-1):
        """Retrieve a list of messages."""
        count = 100  # Number of messages to fetch per request
        fetched_messages = 0  # Counter for fetched messages
        page_token = None  # Token for pagination

        while True:
            # Adjust count if maximum_messages is specified
            if maximum_messages != -1 and fetched_messages + count > maximum_messages:
                count = maximum_messages - fetched_messages

            # Call the Gmail API to list messages
            response = self.service.users().messages().list(userId=user_id, maxResults=count,
                                                            pageToken=page_token).execute()
            messages = response.get('messages', [])

            # Store the fetched messages in the dictionary
            for message in messages:
                self.mails[message['id']] = message  # Store message ID and details

            # Update the count of fetched messages
            fetched_messages += len(messages)

            # Get the next page token
            page_token = response.get('nextPageToken')

            # Break the loop if there are no more pages or if maximum_messages limit is reached
            if not page_token or (maximum_messages != -1 and fetched_messages >= maximum_messages):
                break



