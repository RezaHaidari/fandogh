from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template
from user.models import ActivationCode


def _get_activation_link(user: User):
    activation_code = ActivationCode.objects.create(user)
    return getattr(settings, "FRONT_ACCOUNT_ACTIVATION_URL").format(
        code=activation_code.code,
        user_id=user.id,
    )


def send_confirmation_email(user: User):
    t = get_template("confirm.html")
    user.email_user(
        subject="Fandogh Email-address confirmation",
        message="",
        from_email=getattr(settings, "EMAIL_FROM"),
        html_message=t.render({
            "activation_link": _get_activation_link(user),
        }),
    )
