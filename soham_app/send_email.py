import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jwt
import datetime


def create_token(email):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload = {"email": email, "exp": expiration}

    # Encode the JWT
    token = jwt.encode(payload, "soham_pass", algorithm="HS256")

    token_url = "http://localhost:8000/reset-password/" + token
    return token_url


def create_html_body(token_url):
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                padding: 20px;
            }}
            .reset-container {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 5px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .reset-button {{
                background-color: #007BFF;
                color: #ffffff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>

    <div class="reset-container">
        <h2>Password Reset Request</h2>
        <p>Hello There,</p>
        <p>We received a request to reset your password. If you didn't make this request, you can safely ignore this email.</p>
        <p>To reset your password, click on the link below:</p>
        <p><strong>Note:</strong> The URL is valid only for 30 minutes</p>
        <a href="{}" style="display: inline-block; background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>Or copy and paste the URL below into your browser:</p>
        <p>Thank you,</p>
        <p>Your Website Team</p>
    </div>

    </body>
    </html>
    '''

    formatted_html = html_template.format(token_url)
    return formatted_html


def send_html_email(email):
    token_url = create_token(email)
    my_email = "ohams2023@gmail.com"
    my_password = "omotpzvdbirayaja"
    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    # Create a MIMEText object to represent the email
    msg = MIMEMultipart("alternative")
    msg["From"] = my_email
    msg["To"] = email
    msg["Subject"] = "Reset Password for Heath Wave Account"

    html_content = create_html_body(token_url)

    # Attach the HTML content to the email
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Upgrade the connection to encrypted SSL/TLS
        server.login(my_email, my_password)
        server.sendmail(my_email, email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: Error: " + str(e))