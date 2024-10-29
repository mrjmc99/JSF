# webhook\scripts.py
import requests



def get_study_details(study_uid,ei_system):
    url = f"https://{ei_system}//pacs/v1/study?studyUid={study_uid}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers,)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get study details: {response.status_code}")

def route_series(series_uid, ei_system,external_system):
    url = f"{ei_system}//pacs/v1/series/routeSeries?seriesUID={series_uid}&aeTitle={external_system}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(url, headers=headers,)
    if response.status_code == 200:
        print(f"Successfully routed series: {series_uid} to {external_system}")
    else:
        raise Exception(f"Failed to route series: {response.status_code}")
