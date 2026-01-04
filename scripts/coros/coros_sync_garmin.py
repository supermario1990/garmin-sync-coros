import json
import os
from ..config import DB_DIR, COROS_FIT_DIR
from ..garmin.garmin_client import GarminClient
from coros_client import CorosClient

SYNC_CONFIG = {
    'GARMIN_AUTH_DOMAIN': '',
    'GARMIN_EMAIL': '',
    'GARMIN_PASSWORD': '',
    'GARMIN_NEWEST_NUM': 0,
    "COROS_EMAIL": '',
    "COROS_PASSWORD": '',
}

def is_time_match(start: float, end: float, garmin_time_list: list) -> bool:
    for garmin_time in garmin_time_list:
        if start >= garmin_time[0] and start <= garmin_time[1]:
            return True
        if end >= garmin_time[0] and end <= garmin_time[1]:
            return True
        if start <= garmin_time[0] and end >= garmin_time[1]:
            return True
    return False


def init():
    if not os.path.exists(COROS_FIT_DIR):
        os.mkdir(COROS_FIT_DIR)

def upload_coros_fit_to_garmin(id, sport_type):
    file = corosClient.downloadActivitie(id, sport_type)
    file_path = os.path.join(COROS_FIT_DIR, f"{id}.fit")
    with open(file_path, "wb") as fb:
        fb.write(file.data)
    upload_status = garminClient.upload_activity(file_path)
    print(f"{id}.fit upload status {upload_status}")

if __name__ == "__main__":
    # 首先读取 面板变量 或者 github action 运行变量
    for k in SYNC_CONFIG:
        if os.getenv(k):
            v = os.getenv(k)
            SYNC_CONFIG[k] = v

    COROS_EMAIL = SYNC_CONFIG["COROS_EMAIL"]
    COROS_PASSWORD = SYNC_CONFIG["COROS_PASSWORD"]
    corosClient = CorosClient(COROS_EMAIL, COROS_PASSWORD)

    GARMIN_EMAIL = SYNC_CONFIG["GARMIN_EMAIL"]
    GARMIN_PASSWORD = SYNC_CONFIG["GARMIN_PASSWORD"]
    GARMIN_AUTH_DOMAIN = SYNC_CONFIG["GARMIN_AUTH_DOMAIN"]
    GARMIN_NEWEST_NUM = SYNC_CONFIG["GARMIN_NEWEST_NUM"]

    garminClient = GarminClient(GARMIN_EMAIL, GARMIN_PASSWORD, GARMIN_AUTH_DOMAIN, GARMIN_NEWEST_NUM)
    garminActivities = garminClient.getAllActivities()
    garmin_time_list = []
    for activity in garminActivities:
        start = activity["beginTimestamp"] / 1000
        end = start + activity["duration"]
        garmin_time_list.append((start, end))

    init()

    all_activities = corosClient.getAllActivities()
    if all_activities == None or len(all_activities) == 0:
        exit()
    for activity in all_activities:
        start = activity["startTime"]
        end = activity["endTime"]
        isMatch = is_time_match(start, end, garmin_time_list)
        activity_id = activity["labelId"]
        sport_type = activity["sportType"]
        if isMatch:
            continue
        else:
            print(json.dumps(activity))
            upload_coros_fit_to_garmin(activity_id, sport_type)
