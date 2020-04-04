import os
import pprint
import random
import datetime
import pickle

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

def links_of_day(service, year, month, day):
    searchBody = {
        "filters": {
            "dateFilter": {
            "dates": [
                {
                "month": month,
                "year": year,
                "day": day
                }
            ]
            }
        },
        "pageSize": 100
        }
    results = service.mediaItems().search(body=searchBody).execute()
    links = [x["productUrl"] for x in results["mediaItems"]]
    return links

def open_links(links):
    # Tried using the webbrowser package but on my computer the firefox it opens doesn't have my logins?
    # Turning to list needed because map gives a lazy iterable
    list(map (lambda x : os.system("xdg-open " + x), links))


def open_links_of_random_day(service):
    (year, month) = random_year_month()
    day = random_day_with_photos(service, year, month)
    links = links_of_day(service, year, month, day)
    open_links(links)

def open_pickle():
    with open("service.file", "rb") as f:
        service = pickle.load(f)
        return service

def save_pickle(service):
    with open("service.file", "wb") as f:
        pickle.dump(service, f, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    #   When running locally, disable OAuthlib's HTTPs verification. When
    #   running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    try:
        service = open_pickle()
        open_links_of_random_day(service)
    except:
        service = get_authenticated_service()
        save_pickle(service)
        open_links_of_random_day(service)
    
    