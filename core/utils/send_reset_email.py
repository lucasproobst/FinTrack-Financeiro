from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_password_reset_email(user, reset_url):
    subject = "Redefinir senha - FinTrack"

    html_content = render_to_string("email/reset_password_email.html", {
        "reset_url": reset_url
    })

    msg = EmailMultiAlternatives(
        subject=subject,
        body="Clique no link para redefinir sua senha: " + reset_url,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
