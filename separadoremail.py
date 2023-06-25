import imaplib
import email
import html2text
from bs4 import BeautifulSoup
import datetime
from dateutil import parser
import time

# IMAP connection configuration
imap_server = 'put you email imap server address'
username = 'your email'
password = 'your password'

# Function to convert HTML to plain text
def convertir_html_a_texto(html):
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    return h.handle(html)

# Function to process email
def procesar_correo(correo):
    # Get the body of the email without HTML format
    cuerpo_correo = ''
    if correo.is_multipart():
        for part in correo.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                cuerpo_correo = part.get_payload(decode=True).decode(part.get_content_charset())
                break
            elif content_type == 'text/html':
                cuerpo_correo = convertir_html_a_texto(part.get_payload(decode=True).decode(part.get_content_charset()))
                break
    else:
        cuerpo_correo = correo.get_payload(decode=True).decode(correo.get_content_charset())

    # Text string in HTML format
    html_string = cuerpo_correo
    # Create a BeautifulSoup object with the HTML string
    soup = BeautifulSoup(html_string, 'html.parser')

    # Extract the text from the HTML content
    texto = soup.get_text()
    texto = texto.strip()

    # Split the text into separate lines
    lineas = texto.split('\n')

    event_type_value = None      #This are the values I want to get from the email body 
    invitee_name_value = None
    invitee_email_value = None
    chapa_number_value = None
    fecha = None
    hora = None

    # Loop through each line
    for i in range(len(lineas)):
        # Check if the line contains "Event Type"
        if "Event Type:" in lineas[i]:
            # Check if there is a next line available
            if i + 1 < len(lineas):
                event_type_value = lineas[i + 3].strip()
            else:
                event_type_value = ""

        if "Invitee:" in lineas[i]:
            # Check if there is a next line available
            if i + 1 < len(lineas):
                invitee_name_value = lineas[i + 3].strip()
            else:
                invitee_name_value = ""

        # Check if the line contains "Invitee Email"
        if "Invitee Email" in lineas[i]:
            # Verifica si hay una línea siguiente disponible
            if i + 1 < len(lineas):
                invitee_email_value = lineas[i + 3].strip()
            else:
                invitee_email_value = ""

        if "Ingrese su numero de Chapa" in lineas[i]:
            # Check if there is a next line available
            if i + 1 < len(lineas):
                chapa_number_value = lineas[i + 3].strip()
            else:
                chapa_number_value = ""
            break

        # Check if the line contains "Event Date/Time"
        if "Event Date/Time" in lineas[i]:
            # Check if there is a next line available
            if i + 1 < len(lineas):
                event_time_value = lineas[i + 3].strip()

                cadena = event_time_value

                # get the time
                hora = cadena.split(" - ")[0]

                # get the date
                fecha_str = cadena.split(" - ")[1].split(" (")[0]
                fecha = datetime.datetime.strptime(fecha_str, "%A, %d %B %Y") #This is the format I get the date

            else:
                event_time_value = ""

    # Perform any specific action with the values ​​extracted from the mail
    print(event_type_value)
    print(invitee_name_value)
    print(invitee_email_value)
    print(chapa_number_value)
    if fecha is not None:
        print(fecha.strftime("%Y-%m-%d")) #This is the format I want to get the date
    if hora is not None:
        print(hora)
    print()

# main loop
while True:
    try:
        #Connection to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)

        # Selection of the mail folder (inbox in this case)
        mail.select('inbox')

        # Search for new unread emails
        status, data = mail.search(None, 'UNSEEN', 'FROM "put here the senders email"')

        # Get the IDs of the found emails
        email_ids = data[0].split()

        # Process each new email
        for email_id in email_ids:
            # Get the content of the mail
            status, data = mail.fetch(email_id, '(RFC822)') #RFC822 is the format of the email

            # Get the body of the mail
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # process the email
            procesar_correo(msg)

        # close the connection
        mail.logout()

        # wait 1 minute before checking again
        time.sleep(30)
    except Exception as e:
        print(f"Error al leer correos electrónicos: {str(e)}")
        # wait 1 minute before trying again
        time.sleep(30)
