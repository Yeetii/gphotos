import os
import pprint
import random
import datetime

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

pp = pprint.PrettyPrinter(indent=2)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def list_photos(service):
  results = service.mediaItems().list().execute()

  pp.pprint(results)
  print(len(results))
  print(len(results["mediaItems"]))

def random_year_month():
    currentYear = datetime.datetime.now().year
    randYear = random.randint(2012, currentYear)
    if (randYear == currentYear):
        maxMonth = datetime.datetime.now().month
    else:
        maxMonth = 12
    randMonth = random.randint(1, maxMonth)
    return (randYear, randMonth)

def random_day_with_photos(service, year, month):
    searchBody = {
        "filters": {
            "dateFilter": {
            "dates": [
                {
                "month": month,
                "year": year,
                "day": 0
                }
            ]
            }
        },
        "pageSize": 100
        }
    results = service.mediaItems().search(body=searchBody).execute()

    creationTimesStrings = [x["mediaMetadata"]["creationTime"] for x in results["mediaItems"]]
    # Builds a set of all days in integer form
    creationDays = set(map(lambda x : int(x[8:10]), creationTimesStrings))
    randomDay = random.sample(creationDays, 1)[0]
    return randomDay

if __name__ == '__main__':
#   When running locally, disable OAuthlib's HTTPs verification. When
#   running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
  service = get_authenticated_service()
  list_photos(service)