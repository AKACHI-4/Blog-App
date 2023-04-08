import smtplib 
from email.mime.text import MIMEText

def sendmail(name, phone, email, message) : 
    port = 2525 
    smtp_server = 'smtp.mailtrap.io'
    login = '18a0938e2a02c3'
    password = 'aacab79c718193'
    mail_message = f"<h3>New message !!</h3> <ul><li>Name: {name}</li><li>Phone no.: {phone}</li><li>Email: {email}</li><li>Message: {message}</li></ul>"


    sender_email = email 
    receiver_email = 'adarshrawat@example.com'

    msg = MIMEText(mail_message, 'html')
    msg['Subject'] = 'Someone wants to contact.'    
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send mail
    with smtplib.SMTP(smtp_server, port) as server : 
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    
    
