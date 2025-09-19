import imaplib, email, re, json

IMAP_SERVER = "imap.gmail.com"   # change as per your email provider
IMAP_PORT = 993

def fetch_emails(username, password, limit=5):
    """Fetch recent emails for user"""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(username, password)
    mail.select("inbox")

    status, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    latest_ids = mail_ids[-limit:]

    emails = []
    for i in latest_ids:
        status, msg_data = mail.fetch(i, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                sender = msg["From"]
                subject = msg["Subject"]

                # Detect unsubscribe link/header
                unsub_link = extract_unsubscribe_link(msg)
                emails.append({
                    "sender": sender,
                    "subject": subject,
                    "unsubscribe_link": unsub_link
                })
    return emails

def extract_unsubscribe_link(msg):
    """Find unsubscribe option in headers or body"""
    # Check List-Unsubscribe header
    if "List-Unsubscribe" in msg:
        return msg["List-Unsubscribe"]

    # Search inside body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode(errors="ignore")
                match = re.search(r'href=[\'"]?([^\'" >]+)', body)
                if "unsubscribe" in body.lower():
                    return match.group(1) if match else None
    return None

def load_blocklist():
    try:
        with open("blocklist.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_blocklist(blocklist):
    with open("blocklist.json", "w") as f:
        json.dump(blocklist, f, indent=4)

def unsubscribe_sender(sender):
    blocklist = load_blocklist()
    if sender not in blocklist:
        blocklist.append(sender)
    save_blocklist(blocklist)
    return True
