import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_gchat_message(text: str):
    url = current_app.config.get('GCHAT_WEBHOOK_URL')
    if not url:
        print(f"[GChat webhook not configured — would send]: {text}")
        return False
    try:
        requests.post(url, json={'text': text}, timeout=10)
        return True
    except requests.RequestException as e:
        print(f"[GChat send failed]: {e}")
        return False


def send_email(to_addr: str, subject: str, html_body: str):
    cfg = current_app.config
    if not cfg.get('MAIL_SERVER') or not cfg.get('MAIL_USERNAME'):
        print(f"[SMTP not configured — would email {to_addr}]: {subject}")
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = cfg['MAIL_USERNAME']
        msg['To'] = to_addr
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP(cfg['MAIL_SERVER'], cfg['MAIL_PORT']) as server:
            server.starttls()
            server.login(cfg['MAIL_USERNAME'], cfg['MAIL_PASSWORD'])
            server.sendmail(cfg['MAIL_USERNAME'], to_addr, msg.as_string())
        return True
    except Exception as e:
        print(f"[Email send failed]: {e}")
        return False
