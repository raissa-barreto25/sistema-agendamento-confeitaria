from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials/google.json'
CALENDAR_ID = 'primary'  # ou o ID da agenda da empresa

def criar_evento_google(agendamento):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    service = build('calendar', 'v3', credentials=credentials)

    inicio = datetime.combine(agendamento.data, agendamento.horario)
    fim = inicio + timedelta(hours=1)  # duração padrão

    evento = {
        'summary': 'Pedido Agendado',
        'description': 'Agendamento realizado pelo sistema',
        'start': {
            'dateTime': inicio.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': fim.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }

    evento_criado = service.events().insert(
        calendarId=CALENDAR_ID,
        body=evento
    ).execute()

    return evento_criado.get('id')
