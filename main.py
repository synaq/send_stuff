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


def exit_with_help():
    print(f"{sys.argv[0]} <recipient_address> [<recipient address> ...]")
    sys.exit(2)


mail_server = os.getenv('SEND_STUFF_MAIL_SERVER')
mail_user = os.getenv('SEND_STUFF_MAIL_USER')
mail_pass = os.getenv('SEND_STUFF_MAIL_PASS')


if not mail_server or not mail_user or not mail_pass:
    print("You must set environment variables with mail sending configuration. Please see README.md")
    sys.exit(1)

opts, args = getopt.gnu_getopt(sys.argv[1:], "h", ["help"])

for opt in opts:
    if "-h" in opt:
        exit_with_help()

if len(args) < 1:
    exit_with_help()

sender = "Send stuff test <willemv@synaq.com>"
recipient = args[0]

message = MIMEMultipart("alternative")
message["From"] = sender
message["To"] = f"Test Recipient <{recipient}>"
message["Subject"] = "Test message from Send Stuff"

html = """\
<html>
  <body>
    <p><b>Send Stuff Mail Test</b></p>
    <p>Test message</p>
    <p>
        <hr />
        This is an email from Send Stuff, used for testing.
    </p>
  </body>
</html>
"""

part = MIMEText(html, "html")
message.attach(part)

text = """\
Send Stuff Mail Test

Test message

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
