from googleapiclient.errors import HttpError
import logging
from typing import List, Optional
from dataclasses import dataclass
import base64
from email.mime.audio       import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base        import MIMEBase
from email.mime.image       import MIMEImage
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
import mimetypes
import os
from enum import Enum
from nanoHUB.domain.interfaces import FileHandler
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


@dataclass
class MessageParameters:
    sender: str
    to: List[str]
    msg_type: "MessageType"
    msg: Optional[str] = None
    subject: str = ''
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    signature: bool = False
    user_id: str = 'me'



class MessageType(Enum):
    HTML = 'html'
    PLAIN = 'plain'


class Message:
    def __init__(self, parameters: MessageParameters):
        self.parameters = parameters

    def create_new(self):
        if self.parameters.attachments:
            attach_plain = MIMEMultipart('alternative')

            if self.parameters.msg_type == MessageType.PLAIN:
                attach_plain.attach(MIMEText(self.parameters.msg, 'plain'))

            attach_html = MIMEMultipart('related')
            if self.parameters.msg_type == MessageType.HTML:
                attach_html.attach(MIMEText(self.parameters.msg, 'html'))

            attach_plain.attach(attach_html)
            msg.attach(attach_plain)


class MessageDecorator:
    def __init__(self, parameters: MessageParameters):
        self.parameters = parameters

    def decorate(self, message: MIMEBase) -> MIMEBase:
        raise NotImplementedError


class CcMessageDecorator(MessageDecorator):
    def decorate(self, message: MIMEBase) -> MIMEBase:
        message['Cc'] = ', '.join(self.parameters.cc)
        return message


class BccMessageDecorator(MessageDecorator):
    def decorate(self, message: MIMEBase) -> MIMEBase:
        message['Bcc'] = ', '.join(self.parameters.bcc)
        return message


class SignatureHtmlMessageDecorator(MessageDecorator):
    def decorate(self, message: MIMEBase) -> MIMEBase:
        # message['Cc'] = ', '.join(self.parameters.cc)
        return message


class SignaturePlainMessageDecorator(MessageDecorator):
    def decorate(self, message: MIMEBase) -> MIMEBase:
        # message['Cc'] = ', '.join(self.parameters.cc)
        return message


class Attachments:
    def __init__(self, parameters: MessageParameters):
        self.parameters = parameters

    def decorate(self, message: MIMEBase) -> MIMEBase:
        if not self.parameters.attachments:
            return message

        return self.attach_to(message, self.parameters.attachments)

    def attach_to(self, message: MIMEBase, attachments: List[str]) -> MIMEBase:
        raise NotImplementedError


class MessageAttachments(Attachments):
    def attach_to(self, message: MIMEBase, attachments: List[str]) -> MIMEBase:
        attach_html = MIMEMultipart('related')
        attach_html.attach(MIMEText(self.parameters.msg_html, 'html'))

        attach_plain = MIMEMultipart('alternative')
        attach_plain.attach(MIMEText(self.parameters.msg_plain, 'plain'))
        attach_plain.attach(attach_html)

        for filepath in attachments:
            content_type, encoding = mimetypes.guess_type(filepath)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            main_type, sub_type = content_type.split('/', 1)
            with open(filepath, 'rb') as file:
                raw_data = file.read()

                attm: MIMEBase
                if main_type == 'text':
                    attm = MIMEText(raw_data.decode('UTF-8'), _subtype=sub_type)
                elif main_type == 'image':
                    attm = MIMEImage(raw_data, _subtype=sub_type)
                elif main_type == 'audio':
                    attm = MIMEAudio(raw_data, _subtype=sub_type)
                elif main_type == 'application':
                    attm = MIMEApplication(raw_data, _subtype=sub_type)
                else:
                    attm = MIMEBase(main_type, sub_type)
                    attm.set_payload(raw_data)

            fname = os.path.basename(filepath)
            attm.add_header('Content-Disposition', 'attachment', filename=fname)
            message.attach(attm)

        return message


# class Gmail:
#     def __init__(self, client, logger: logging.Logger):
#         self.client = client
#         self.message_
#         self.logger = logger
#
#     def send_message(self, msg_params: Message):
#         try:
#             message = (self.client.users().messages().send(userId=msg_params.user_id, body=msg_params.get_message())
#                        .execute())
#             self.logger.info('Message Id: %s' % message['id'])
#             return message
#         except HttpError as error:
#             self.logger.info('An error occurred when sending the message: %s' % error)


class GoogleApiFactory:
    def __init__(self, credentials_file_path: str, scopes: str, service_type: str, version: str):
        self.credentials_file_path = credentials_file_path
        self.scopes = scopes
        self.service_type = service_type
        self.version = version

    def create_new_service(self, root_dir: str):
        credentials_file_path = root_dir + '/' + self.credentials_file_path
        with open(credentials_file_path) as f:
            json_key = json.load(f)

        credentials = Credentials.from_service_account_info(
            json_key, scopes=self.scopes.split(",")
        )

        return build(self.service_type, self.version, credentials=credentials, cache_discovery=False)
