from celery import shared_task
from django.core.mail import EmailMessage, BadHeaderError
import smtplib


@shared_task(
    bind = True,
    soft_time_limit = 25,
    time_limit = 30,
    expires = 120,
    max_retries = 3,
    autoretry_for=(smtplib.SMTPException, ConnectionError, TimeoutError)
)
def send_email_via_mailru(self,recipient, message, subject):
    """Отправить сообщение на email"""
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            to=[recipient],
        )
        email.send(fail_silently=False)
        print(f"✅ Письмо успешно отправлено на {recipient}")
        return True
        
    except (smtplib.SMTPException, ConnectionError, TimeoutError) as exc:
        print(f"⚠️ Сетевая ошибка при отправке на {recipient}: {exc}")
        raise self.retry(exc=exc)
        
    except BadHeaderError as exc:
        print(f"❌ Ошибка заголовков для {recipient}: {exc}")
        return False
        
    except Exception as e:
        print(f"❌ Неизвестная ошибка для {recipient}: {e}")
        raise self.retry(exc=e)
        

def send_email_via_mailru_with_attachment(recipient, message, subject, attachments=None):
    try:
        
        email = EmailMessage(
            subject=subject,
            body=message,
            to=[recipient],
        )
        
        successful_attachments = 0
        if attachments:
            for attachment_data in attachments:
                try:
                    filename = attachment_data.get('filename', 'file.bin')
                    file_content = attachment_data.get('content', b'')
                    content_type = attachment_data.get('content_type', 'application/octet-stream')
                    
                    # Проверяем, что content - bytes
                    if isinstance(file_content, str):
                        file_content = file_content.encode('utf-8')
                    
                    # Прикрепляем файл
                    email.attach(filename, file_content, content_type)
                    successful_attachments += 1
                    
                except Exception as e:
                    continue
        
        # Отправляем email
        email.send(fail_silently=False)
        return True
            
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")



@shared_task
def mass_mailing(recipients_data):
    """Массовая расслыка"""
    sent = 0
    failed = 0
    
    for data in recipients_data:
        try:
            email = EmailMessage(
                subject=data['subject'],
                body=data['message'],
                to=[data['email']],
            )
            email.send(fail_silently=False)
            sent += 1
        except Exception:
            failed += 1
    
    return {'sent': sent, 'failed': failed}