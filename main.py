import flask
from flask import make_response, request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import firebase_admin
from firebase_admin import credentials, auth
from email.utils import parseaddr
import urllib.parse

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ settings

DEEPLINK_DOMAIN_NAME = 'www.virtualscape.cloud'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_LOGIN = 'mailer.virtualscape'
SMTP_PASSWORD = 'rpkuvqyclqutqqge'

SERVICE_MAIL = "mailer.virtualscape@gmail.com"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ script constants
# possible email custom actions
ACTION_VERIFY_EMAIL = 'verify-email'
ACTION_RESET_PASSWORD = 'reset-password'


# all possible responses from API (also can return firebase error message text)
RESPONSE_STATUS_ERROR = 'error'
RESPONSE_STATUS_ERROR_NO_USER = 'no_user'

RESPONSE_STATUS_EMAIL_SENT = 'sent'
RESPONSE_STATUS_VERIFIED = 'success'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ setup firebase admin sdk

cred = credentials.Certificate("firebase_service.json")
firebase_admin.initialize_app(cred)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = flask.Flask('firebase-admin')

methods = ['GET']

# -------------------------------------------------------------------
# verify user by token from email
@app.route('/index', methods=methods)
def index_run():
    return my_response('Firebase admin server is running')

# -------------------------------------------------------------------
# verify user by token from email
@app.route('/verify-email', methods=methods)
def verify_email():
    print('verify email')
    try:
        id_token = request.args.get('id_token')

        claims = auth.verify_id_token(id_token, clock_skew_in_seconds=10)

        if ('action' in claims) and (claims['action'] == ACTION_VERIFY_EMAIL):

            user_id = claims['user_id']

            user = auth.update_user(
                    user_id,
                    email_verified=True
                )

            return my_response(RESPONSE_STATUS_VERIFIED)
        else:
            print('Email claim BAD ACTION')

    except Exception as e:
        print(f'ex: {str(e)}')

    return my_response(RESPONSE_STATUS_ERROR)


# -------------------------------------------------------------------
@app.route('/send-confirm-email', methods=methods)
def confirm_email():

    try:
        name, email = parseaddr(request.args.get('email'))

        if email is None:
            return 'incorrect email'

        user = auth.get_user_by_email(email)
        print('Successfully fetched user data: {0}'.format(user.uid))

        uid = user.uid
        additional_claims = {
            'user_id' : uid,
            'action': ACTION_VERIFY_EMAIL
        }
        custom_token = auth.create_custom_token(uid, additional_claims)


        # create message object instance
        msg = MIMEMultipart()

        FROM = SERVICE_MAIL
        TO = email
        SUBJECT = f"Email Verification"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = FROM
        msg['To'] = TO

        import urllib.parse
        safe_token = urllib.parse.quote_plus(custom_token)

        html = f"""\
            <html>
              <head></head>
              <body>
                <h4>Need email verification</h4>
                </br>
                Click the link below to verify email
                <a href="https://{DEEPLINK_DOMAIN_NAME}/verify?action=verifyEmail&token={safe_token}">Click to Verify</a>
               
              </body>
            </html>
            """

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        server = smtplib.SMTP_SSL(SMTP_SERVER, 465)
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()

        return my_response(RESPONSE_STATUS_EMAIL_SENT)

    except Exception as e:
        print(f'exception: {str(e)}')
        return str(e)


    return my_response(RESPONSE_STATUS_ERROR)

# -------------------------------------------------------------------
@app.route('/send-change-password-email', methods=methods)
def send_change_password_email():

    print("\nChange password request: sending email code\n")

    try:
        name, email = parseaddr(request.args.get('email'))

        if email is None:
            return 'incorrect email'

        user = auth.get_user_by_email(email)

        if user is None:
            print('user not registered')
            return my_response(RESPONSE_STATUS_ERROR_NO_USER)

        print('Successfully fetched user data: {0}'.format(user.uid))

        uid = user.uid
        additional_claims = {
            'user_id' : uid,
            'action': ACTION_RESET_PASSWORD
        }
        custom_token = auth.create_custom_token(uid, additional_claims)


        # create message object instance
        msg = MIMEMultipart()

        FROM = SERVICE_MAIL
        TO = email
        SUBJECT = f"Change Password Request"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = FROM
        msg['To'] = TO

        safe_token = urllib.parse.quote_plus(custom_token)

        html = f"""\
            <html>
              <head></head>
              <body>
                <h4>Change password request</h4>
                </br>
                Click the link below to change password:
                <a href="https://{DEEPLINK_DOMAIN_NAME}/verify?action=changePassword&changepwd_token={safe_token}">Change password</a>
               
              </body>
            </html>
            """

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        server = smtplib.SMTP_SSL(SMTP_SERVER, 465)
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()

        return my_response(RESPONSE_STATUS_EMAIL_SENT)

    except Exception as e:
        print(f'exception: {str(e)}')
        return str(e)

    return my_response(RESPONSE_STATUS_ERROR)


# -------------------------------------------------------------------
def my_response(txt):
    response = make_response(txt, 200)
    response.mimetype = "text/plain"
    return response

if __name__ == '__main__':
    app.run()