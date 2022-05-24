# Created by saxenap at 5/17/22
import logging
from sendgrid.helpers.mail import *


class SendGrid:
    def __init__L(self, client: sendgrid.SendGridAPIClient, logger: logging.Logger):
        self.client = client
        self.logger = logger

    def send(self, ):

class SendGridClientFactory:
    def create_new_with(self, api_key: str, logger: logging.Logger):
        client = sendgrid.SendGridAPIClient(api_key)
        return SendGrid(client, logger)


sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("test@example.com")
to_email = To("test@example.com")
subject = "Sending with SendGrid is Fun"
content = Content("text/plain", "and easy to do anywhere, even with Python")
mail = Mail(from_email, to_email, subject, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers)