from google.appengine.api import mail


ADMINS = [("Ragil Prasetya", "praser05@gmail.com"),
          ("Giri Kuncoro", "girikuncoro@gmail.com")]

FROM_MAIL = "Communicate Indonesia Support <fallback@ci.com>"
SUBJECT = "Fallback alert for Communicate Indonesia service"

BODY = "Dear Admin:\n\n"
"Our Communication Indonesia service is having issues.\n"
"Please fix this.\n\n"
"Thanks and cheers.\n"


def notify_admin():
    for admin in ADMINS:
        to_mail = "{} <{}>".format(admin[0], admin[1])

        mail.send_mail(to=to_mail,
                       sender=FROM_MAIL,
                       subject=SUBJECT,
                       body=BODY)
