try:
    import win32com.client
except:
    pass
import logging

logger = logging.getLogger(__name__)

def send_email(subject, html_body, recipeint, attachment=None):
    """
    Send email via Outlook
    
    Parameters
    ----------
    subject : string
        Subject text
        
    html_body : string
        HTML body text
    
    recipeint : string
        Email address or addresses, separated by semicolon
    
    attachment : string
        Name of file to attached (with full path)
    """
    logger.info("Sending email")
    
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = subject
    newMail.HTMLBody = html_body
    newMail.To = recipeint
    if attachment:
        newMail.Attachments.Add(attachment)
    newMail.Send()