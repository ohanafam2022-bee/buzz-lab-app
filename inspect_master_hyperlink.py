from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BtolneaNSnEbJlPGwwDm2WL6gJ86sUNtmj7AszT9v7U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def check_master():
    service = get_service()
    
    # Fetch values (default render option: FORMATTED_VALUE)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Master!A2:D').execute()
    rows = result.get('values', [])
    
    print("\n--- Master Sheet Content (FORMATTED_VALUE) ---")
    for row in rows:
        print(row)

    # Fetch values (render option: UNFORMATTED_VALUE) maybe? No, let's see formula
    # To see formula, we need valueRenderOption='FORMULA'
    result_formula = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range='Master!D2:D', 
        valueRenderOption='FORMULA'
    ).execute()
    formulas = result_formula.get('values', [])
    
    print("\n--- Master Sheet Column D Formulas ---")
    for row in formulas:
        print(row)

if __name__ == "__main__":
    check_master()
