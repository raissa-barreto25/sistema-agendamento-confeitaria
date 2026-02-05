from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials/google.json'
CALENDAR_ID = 'primary'
TIMEZONE = 'America/Sao_Paulo'


def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)


# -------------------------
# CRIAR EVENTO
# -------------------------
def criar_evento_google(pedido):
    service = get_calendar_service()

    inicio = datetime.combine(pedido.data_entrega, datetime.min.time()).replace(hour=9)
    fim = inicio + timedelta(hours=1)

    evento = {
        'summary': f'Pedido #{pedido.id}',
        'description': 'Entrega agendada pelo sistema',
        'start': {
            'dateTime': inicio.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': fim.isoformat(),
            'timeZone': TIMEZONE,
        },
    }

    evento_criado = service.events().insert(
        calendarId=CALENDAR_ID,
        body=evento
    ).execute()

    return evento_criado['id']


# -------------------------
# ATUALIZAR EVENTO
# -------------------------
def atualizar_evento_google(evento_id, pedido):
    service = get_calendar_service()

    evento = service.events().get(
        calendarId=CALENDAR_ID,
        eventId=evento_id
    ).execute()

    inicio = datetime.combine(pedido.data_entrega, datetime.min.time()).replace(hour=9)
    fim = inicio + timedelta(hours=1)

    evento['start']['dateTime'] = inicio.isoformat()
    evento['end']['dateTime'] = fim.isoformat()

    service.events().update(
        calendarId=CALENDAR_ID,
        eventId=evento_id,
        body=evento
    ).execute()


# -------------------------
# CANCELAR EVENTO
# -------------------------
def cancelar_evento_google(evento_id):
    service = get_calendar_service()

    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=evento_id
    ).execute()
