import os
import getopt
import ssl
import sys
import smtplib
import uuid
import numpy as np
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
from faker import Faker


def exit_with_help():
    print(f"{sys.argv[0]} <sender> <recipient_address> [<recipient address> ...]")
    sys.exit(2)


mail_server = os.getenv('SEND_STUFF_MAIL_SERVER')
mail_user = os.getenv('SEND_STUFF_MAIL_USER')
mail_pass = os.getenv('SEND_STUFF_MAIL_PASS')

fake = Faker()
fake_text = Faker(locale='la')

if not mail_server or not mail_user or not mail_pass:
    print("You must set environment variables with mail sending configuration. Please see README.md")
    sys.exit(1)

opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help"])

for opt in opts:
    if "-h" in opt:
        exit_with_help()

if len(args) < 2:
    exit_with_help()

sender_email = args[0]
recipient = args[1]

sender_name = fake.name()
sender = f"{sender_name} <{sender_email}>"
sender_position = fake.job()
sender_company = fake.company()
sender_address = fake.address()


message = MIMEMultipart("alternative")
message["From"] = sender
message["To"] = f"{fake.name()} <{recipient}>"
message["Subject"] = fake.bs()
message.add_header('reply-to', f"{sender_name} <{fake.safe_email()}>")

message_title = fake.text()
message_content = fake_text.paragraphs()
message_content_html = "<p>" + "</p><p>".join(message_content) + "</p>"
message_content_plain = "\r\n\r\n".join(message_content)

html = f"""\
<html>
  <body>
    <p>{message_title}</p>
    {message_content_html}
    
    <p>
        <hr >
        <strong>{sender_name}</strong><br />
        {sender_position}<br /><br />
        <strong>{sender_company}<strong><br />
        {sender_address}
    </p
    <p>
        <hr />
        This is an email from Send Stuff, used for testing.
    </p>
  </body>
</html>
"""

part = MIMEText(html, "html")
message.attach(part)

text = f"""\
{message_title}

{message_content_plain}

--
{sender_name}
{sender_position}

{sender_company}
{sender_address}

--
This is an email from Send Stuff, used for testing.
"""

part = MIMEText(text)
message.attach(part)
file_name = f"/tmp/{uuid.uuid4()}.jpg"

Image.effect_mandelbrot((800, 600), tuple(np.random.rand(1, 4)[0]+np.array([-2.5, -2, 0.5, 1])), 100).save(file_name)

with open(file_name, "rb") as pic:
    part = MIMEBase("image", "jpg")
    part.set_payload(pic.read())

os.remove(file_name)

encoders.encode_base64(part)

part.add_header(
    "Content-Disposition",
    "attachment", filename=os.path.basename(file_name)
)

message.attach(part)

context = ssl.create_default_context()

with smtplib.SMTP(mail_server) as server:
    server.starttls(context=context)
    server.login(mail_user, mail_pass)
    server.sendmail(sender, recipient, message.as_string())
