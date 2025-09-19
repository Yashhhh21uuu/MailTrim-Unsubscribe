import imaplib, smtplib, ssl, email
from email.header import decode_header
from email.message import EmailMessage

class MailTrimClient:
    def __init__(self, email, imap_server="mail.tvisha.in", smtp_server="mail.tvisha.in"):
        self.email = email
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.imap_port = 993
        self.smtp_port = 465
        self.mail = None

    def login(self, password):
        """Login to IMAP using email + password"""
        self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        self.mail.login(self.email, password)
        print("✅ Logged in successfully")

    def fetch_unseen(self, limit=5):
        """Fetch unseen emails (fallback to ALL if needed)"""
        self.mail.select("inbox")
        status, messages = self.mail.search(None, "UNSEEN")  # Use UNSEEN for unread only

        if status != "OK":
            print("❌ Failed to search inbox")
            return []

        print("Search status:", status)
        print("Raw messages:", messages)

        ids = messages[0].split()
        if not ids:
            print("📭 No unseen emails found")
            return []

        results = []
        for eid in ids[-limit:]:
            _, msg_data = self.mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            # Decode subject
            subject, encoding = decode_header(msg.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            results.append({"from": msg.get("From"), "subject": subject})

        return results

    def send_auto_response(self, password, to_email, subject):
        """Send an auto-response email"""
        msg = EmailMessage()
        msg["From"] = self.email
        msg["To"] = to_email
        msg["Subject"] = f"Re: {subject}"
        msg.set_content("Hello,\n\nThis is an automated response.\n\n– MailTrim")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
            server.login(self.email, password)
            server.send_message(msg)
        print(f"✅ Auto-response sent to {to_email}")
