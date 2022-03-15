# Send Stuff

Send Stuff generates a flood of random emails, as many as you specify with the `-i` (iterations)
parameter, or just one, if `-i` is omitted.

It is intended as a simple way to generate test email traffic, for development, stress testing
or demonstration of email or email-related systems, with test data which will resemble real
traffic.

The script will generate the following at random:
* Sender display name
* Recipient display name
* Message subject
* Message content (English title, followed by a few paragraphs of lorem ipsum)
* A signature for the sender, with or without a randomly generated logo (for some messages)
* A randomly generated fractal image as an attachment (for some messages)

Logos and attachments are not always added, to create diversity in the structure of the traffic.

**This tool is not intended to be used to send bulk email, and will clearly identify its traffic
as intended for testing only.**

## Running in Docker

**To send via an SMTP server with authentication:**
````
docker run -it --rm -e SEND_STUFF_MAIL_SERVER=your.smtp.host -e SEND_STUFF_MAIL_USER="your.username@domain.com" -e SEND_STUFF_MAIL_PASS="Your.Password" synaq/send_stuff -i <iterations> sender@domain.com some.recipient@domain.com another.recipient@domain.com
````

In this mode, sender display names will be faked at random, but the sender will always be
the address specified on the command line.

**To dump directly to an SMTP listener (no authentication):**

````
docker run -it --rm synaq/send_stuff -s direct.host.com -i <iterations> sender@domain.com some.recipient@domain.com another.recipient@domain.com
````

In this mode, the envelope from address of the sender will also be faked at random.

## Running locally

1) Install `miniforge` in which ever way is recommended for your operating system.

2) Create the environment while in the project directory:

```
conda env create --prefix=./env
``` 

3) Activate the environment

```
conda activate ./env
```

4) Set up environment variables for configuration:

```
cp set_environment_variables.sh.dist set_environment_variables.sh
```

Populate the file with appropriate configuration for sending mail, then before running
the script:

```
source set_environment_variables.sh
```

5) Run the script

```
python main.py -i <iterations> sender@domain.com some.recipient@domain.com another.recipient@domain.com
```