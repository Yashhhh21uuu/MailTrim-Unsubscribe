from mailtrim_sdk.client import MailTrimClient
import getpass

email = input("Enter your MailTrim email: ")
password = getpass.getpass(f"Enter password for {email}: ")

client = MailTrimClient(email=email)
client.login(password)

emails = client.fetch_unseen(limit=3)
for e in emails:
    print(f"📧 {e['from']} → {e['subject']}")
