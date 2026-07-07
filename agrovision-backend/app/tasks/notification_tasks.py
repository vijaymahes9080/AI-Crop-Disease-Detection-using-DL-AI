from app.core.cel_app import celery_app

@celery_app.task
def send_outbreak_alert(user_id_str: str, message: str):
    print(f"[*] Sending alert to User {user_id_str}: {message}")
    # Integration logic with Firebase Cloud Messaging / SMS Gateway triggers here
    return True
