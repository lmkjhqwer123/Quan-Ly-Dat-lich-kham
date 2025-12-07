
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(recipient_email, subject, body):
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Email credentials are not set in environment variables.")
        return False

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_reset_password_email(recipient_email, reset_link):
    subject = "Yêu Cầu Đặt Lại Mật Khẩu - Umbrella Medical"
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2563eb, #1e40af); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; border-radius: 0 0 10px 10px; }}
            .message {{ margin-bottom: 20px; }}
            .button-container {{ text-align: center; margin: 30px 0; }}
            .reset-button {{ display: inline-block; background: #2563eb; color: white; padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
            .reset-button:hover {{ background: #1d4ed8; }}
            .link-fallback {{ margin-top: 20px; word-break: break-all; color: #666; font-size: 12px; }}
            .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #e5e7eb; }}
            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Đặt Lại Mật Khẩu</h1>
            </div>
            <div class="content">
                <div class="message">
                    <p>Xin chào,</p>
                    <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Umbrella Medical của mình. Nhấp vào nút bên dưới để tiếp tục.</p>
                </div>
                
                <div class="button-container">
                    <a href="{reset_link}" class="reset-button">Xác Nhận & Đặt Lại Mật Khẩu</a>
                </div>
                
                <div class="link-fallback">
                    <p>Hoặc sao chép liên kết này vào trình duyệt:</p>
                    <p>{reset_link}</p>
                </div>
                
                <div class="warning">
                    <p><strong>⏰ Lưu ý:</strong> Liên kết này sẽ hết hạn trong <strong>15 phút</strong>. Nếu bạn không yêu cầu điều này, vui lòng bỏ qua email này.</p>
                </div>
                
                <p style="margin-top: 30px; color: #666;">
                    Nếu bạn gặp vấn đề, hãy liên hệ với bộ phận hỗ trợ của chúng tôi.<br>
                    Cảm ơn,<br>
                    <strong>Đội Ngũ Umbrella Medical</strong>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Umbrella Medical. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(recipient_email, subject, body)
