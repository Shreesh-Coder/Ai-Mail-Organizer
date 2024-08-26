import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from OAuth import authentication
import base64
import quopri
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def create_thread(id, messages):    
    return {
        "id" : "",
        "messages" : messages
    }

def create_message(id, headers, body,attachment, labelsID):
    # Header Structure
    # {
    #         "Subject": subject,
    #         "Cc": cc,
    #         "Date": date,
    #         "From": from_email,
    #         "To": to
    #     }
    return {
        "id": id,
        "headers": headers,
        "labelsIds" : labelsID,
        "body": body,
        "attachment": None
    }

threads = []

def show_chatty_threads():
#   creds, _ = google.auth.default()
    creds = authentication(SCOPES)
    try:
        service = build("gmail", "v1", credentials=creds)
        threads = service.users().threads().list(userId="me").execute().get("threads", [])
        for thread in threads:
            messages = []
            tdata = service.users().threads().get(userId="me", id=thread["id"]).execute()
            for message in tdata["messages"]:                
                                             
                msgHeader = {}
                payload = message["payload"]
                headers = payload["headers"]

                for header in headers:
                    if header["name"] in ["Subject", "To", "Cc", "Date", "From"]:
                        msgHeader[header["name"]] = header["value"]
                body = ""
                if "parts" in payload:
                    for part in payload["parts"]:
                        body = decode(part, service, message['id'])

                messages.append(create_message(message["id"], msgHeader, body, message["labelIDs"] ))
                
            break
    except HttpError as error:
        print(f"An error occurred: {error}")


def decode(part, service=None, message_id=None):
    # Check for nested parts (e.g., in multipart messages)
    if "parts" in part:
        for sub_part in part["parts"]:
            decode(sub_part, service, message_id)  # Recursively decode parts
        return
    msgAttachment = None
    if "body" in part and ("data" in part["body"] or "attachmentId" in part["body"]):
        if "data" in part["body"]:
            data = part["body"]["data"]
        else:  # Fetch attachment if there's an attachmentId instead of inline data
            if service and message_id:                
                attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=part["body"]["attachmentId"]).execute()
                data = attachment["data"]
                msgAttachment = {
                    "filename": part["filename"],
                    "mimeType": part["mimeType"],     
                    "data": None               
                }
            else:
                return "No service or message ID provided for attachment retrieval."
    else:
        return "No data or attachment ID found in part."

    # Determine if the part is textual or binary based on MIME type
    is_text = part["mimeType"].startswith("text/")

    # Determine encoding
    encoding = None
    for header in part["headers"]:
        if header["name"].lower() == "content-transfer-encoding":
            encoding = header["value"]
            break

    # Decode data
    decoded_data = decode_data(data, encoding, is_text)

    # Handle image saving
    if part["mimeType"].startswith("image/"):
        # Assuming you want to save the image in the current working directory with a filename derived from the partId
        filename = f"{part['partId'].replace('.', '_')}.png"  # Customize this line as needed
        msgAttachment["data"] = decode_data
        with open(filename, "wb") as img_file:
            img_file.write(decoded_data)
        print(f"Image saved as {filename}")
        return

    return (decode_data, msgAttachment)
  

# The decode_data function and other parts of the script remain the same.

def decode_data(encoded_data, encoding, is_text):
    # Decode the data
    if encoding == "base64":
        decoded_data = base64.urlsafe_b64decode(encoded_data + '===')
    elif encoding == "quoted-printable":
        decoded_data = quopri.decodestring(base64.urlsafe_b64decode(encoded_data + '==='))
    else:
        decoded_data = encoded_data

    # If the content is textual, convert it to a string
    if is_text:
        try:
            return decoded_data.decode('utf-8')
        except UnicodeDecodeError:
            print("Error decoding text data; it may not be UTF-8 encoded.")
            return None  # Or handle the error as appropriate for your needs
    else:
        # For non-text content, return the binary data directly
        return decoded_data
 # Return bytes for binary data

if __name__ == "__main__":
    show_chatty_threads()