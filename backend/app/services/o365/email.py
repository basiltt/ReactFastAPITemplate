import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

from O365 import Account
from loguru import logger
from starlette.requests import Request

from backend.app.core.config import settings
from backend.app.models.mail.email import EmailModel


async def send_email_smtp(email: EmailModel, request: Request):
    recipients = ";".join(email.recipients)
    server = smtplib.SMTP(
        request.app.state.settings.smtp_server, request.app.state.settings.smtp_port
    )
    message = MIMEMultipart()
    message["From"] = request.app.state.settings.email_sender
    message["To"] = recipients
    message["Subject"] = email.subject
    message_text = MIMEText(email.message)
    message.attach(message_text)
    if email.attachments:
        for attachment in email.attachments:
            with open(attachment, "r") as f:
                part = MIMEApplication(f.read(), Name=basename(attachment))
            part[
                "Content-Disposition"
            ] = f'attachment; filename="{basename(attachment)}"'
            message.attach(part)
    server.sendmail(settings.email_sender, recipients, message.as_string())
    return {"detail": "Email sent successfully!"}


async def send_email(email_model: EmailModel, request: Request) -> any:
    account = Account(
        (
            request.app.state.settings.o365_client_id,
            request.app.state.settings.o365_client_secret,
        )
    )
    # if not account.is_authenticated:
    #     account.authenticate(scopes=['basic', 'offline_access', 'User.Read', 'User.ReadBasic.All', 'Mail.Read',
    #                                  'Mail.Read.Shared', 'Mail.ReadBasic', 'Mail.ReadBasic.Shared', 'Mail.ReadWrite',
    #                                  'Mail.ReadWrite.Shared', 'Mail.Send', 'Mail.Send.Shared'])
    try:
        message = account.new_message()
        message.to.add(email_model.recipients)
        message.subject = email_model.subject
        message.body = email_model.message
        message.send()
        return {"detail": "Email sent successfully!"}
    except Exception as e:
        logger.error(
            f"Error sending email via O365: {e.args}. Hence sending email via SMTP"
        )
        error_email = EmailModel(
            subject="Q2O Error: Unable to send email via O365",
            message=f"Error sending email via O365: {e.args}. "
            "Check O365 credentials or token file is valid.",
            recipients=[request.app.state.settings.email_sender],
        )
        await send_email_smtp(error_email, request)
        return await send_email_smtp(email_model, request)
