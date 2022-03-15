import os
import getopt
import random
import ssl
import sys
import smtplib
import uuid
import numpy as np
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageDraw
from faker import Faker
from progress.bar import IncrementalBar


def exit_with_help():
    print(f"{sys.argv[0]} [-s server.override.host] [-i iterations] <sender> <recipient_address> [<recipient address> ...]")
    sys.exit(2)


mail_server = os.getenv('SEND_STUFF_MAIL_SERVER')
mail_user = os.getenv('SEND_STUFF_MAIL_USER')
mail_pass = os.getenv('SEND_STUFF_MAIL_PASS')
server_override = None

fake = Faker()
fake_text = Faker(locale='la')

opts, args = getopt.gnu_getopt(sys.argv[1:], "hs:i:", ["help", "server=", "iterations="])

iterations = 1

for opt, val in opts:
    if "-h" in opt:
        exit_with_help()

    if "-s" in opt:
        server_override = val

    if "-i" in opt:
        iterations = int(val)

if len(args) < 2:
    exit_with_help()

if not server_override and (not mail_server or not mail_user or not mail_pass):
    print("You must set environment variables with mail sending configuration or use server override. Please see README.md")
    sys.exit(1)

sender_email = args[0]
recipient = args[1]

bar = IncrementalBar(max=iterations)

file_name = None
logo_cid = None
logo_path = None
sender = None
sender_name = None
sender_position = None
sender_company = None
sender_address = None
fake_sender = None


def purge_logo_file():
    if logo_path is not None:
        os.remove(logo_path)


def purge_attachment_file():
    if file_name is not None:
        os.remove(file_name)


add_logo = False


if iterations > 1:
    bar.start()

for i in range(0, iterations):
    if iterations > 1:
        bar.next()

    reuse_sender = random.choice([True, False])

    if sender_name is None or not reuse_sender:
        sender_name = fake.name()
        sender = f"{sender_name} <{sender_email}>"
        sender_position = fake.job()
        sender_company = fake.company()
        sender_address = fake.address()
        add_logo = random.choice([True, False])
        fake_sender = f"{sender_name} <{fake.safe_email()}>"

    message = MIMEMultipart("related" if add_logo else "alternative")
    message["From"] = sender if not server_override else fake_sender
    message["To"] = f"{fake.name()} <{recipient}>"
    message["Subject"] = fake.bs()

    if not server_override:
        message.add_header('Reply-to', fake_sender)

    message_title = fake.text()
    message_content = fake_text.paragraphs()
    message_content_html = "<p>" + "</p><p>".join(message_content) + "</p>"
    message_content_plain = "\r\n\r\n".join(message_content)

    if add_logo:
        if logo_cid is None or not reuse_sender:
            purge_logo_file()

            logo_cid = uuid.uuid4()
            logo_path = f"/tmp/{logo_cid}.png"
            logo_img = Image.new('RGB', (200, 30), color=(255, 255, 255))
            logo_drawing = ImageDraw.Draw(logo_img)
            logo_drawing.text((10, 10), sender_company, fill=(random.randint(0, 168), random.randint(0, 168), random.randint(0, 168)))
            logo_img.save(logo_path)

        with open(logo_path, 'rb') as logo_file:
            logo_part = MIMEImage(logo_file.read())
            logo_part.add_header('Content-ID', f"<{logo_cid}>")

        message.attach(logo_part)
        logo_html = f"<img src='cid:{logo_cid}' /><br />"
    else:
        logo_html = ""

    html = f"""\
    <html>
      <body>
        <p>{message_title}</p>
        {message_content_html}
        
        <p>
            <hr >
            <strong>{sender_name}</strong><br />
            {sender_position}<br /><br />
            {logo_html}
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

    html_part = MIMEText(html, "html")

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

    text_part = MIMEText(text)

    if add_logo:
        message.preamble = '====================================================='
        message_alternative = MIMEMultipart('alternative')
        message_alternative.attach(html_part)
        message_alternative.attach(text_part)
        message.attach(message_alternative)
    else:
        message.attach(html_part)
        message.attach(text_part)

    add_attachment = random.choice([True, False])
    reuse_attachment = random.choice([True, False])

    if add_attachment:
        if file_name is None or not reuse_attachment:
            purge_attachment_file()

            file_name = f"/tmp/{uuid.uuid4()}.jpg"
            Image.effect_mandelbrot((800, 600), tuple(np.random.rand(1, 4)[0]+np.array([-2.5, -2, 0.5, 1])), 100).save(file_name)

        with open(file_name, "rb") as pic:
            part = MIMEBase("image", "jpg")
            part.set_payload(pic.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            "attachment", filename=os.path.basename(file_name)
        )

        message.attach(part)

    context = ssl.create_default_context()

    if server_override:
        mail_server = server_override

    with smtplib.SMTP(mail_server) as server:
        if not server_override:
            server.starttls(context=context)
            server.login(mail_user, mail_pass)

        server.sendmail(sender, recipient, message.as_string())

if iterations > 1:
    bar.finish()

purge_logo_file()
purge_attachment_file()