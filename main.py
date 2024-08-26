from OAuth import authentication
from threadclient import ThreadClient
from gmailclient import GmailClient


if __name__ == "__main__":
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = authentication(SCOPES)
    thread_client = ThreadClient(creds)

    thread_client.fetch_threads("me", 1)


    thread_client.fetch_all_messages_from_threads("me", 2)
    thread_client.print_threads_messages()
