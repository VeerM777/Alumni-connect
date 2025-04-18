"""
Configuration settings for the Alumni Connect Portal
"""

EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    # Note: Do not store passwords in this file in a production environment
}

# Helper function to send emails
def send_email(from_email, to_email, subject, message, password=None):
    """Send an email using the configured settings"""
    import smtplib
    from email.message import EmailMessage
    from tkinter import messagebox
    
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(message)
        
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as smtp:
            if EMAIL_CONFIG["use_tls"]:
                smtp.starttls()
            
            if password is None:
                password = messagebox.askstring("Email Password", 
                                             f"Enter password for {from_email}:", 
                                             show="*")
            if not password:
                return False, "Password not provided"
                
            smtp.login(from_email, password)
            smtp.send_message(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)