import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_otp_email(to_email, otp):
        """
        Send OTP email to user
        
        Args:
            to_email: Recipient email
            otp: One Time Password
            
        Returns:
            bool: True if sent successfully
        """
        if not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
            print("SMTP credentials not configured. OTP: ", otp)
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.SMTP_SENDER_EMAIL
            msg['To'] = to_email
            msg['Subject'] = "Your Login OTP"
            
            body = f"""
            <html>
                <body>
                    <h2>Login Verification</h2>
                    <p>Your One Time Password (OTP) is:</p>
                    <h1>{otp}</h1>
                    <p>This OTP is valid for 5 minutes.</p>
                    <p>If you did not request this, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(Config.SMTP_SENDER_EMAIL, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            # For dev/testing if email fails, print OTP
            print(f"DEV MODE OTP: {otp}")
            return False
