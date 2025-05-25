from apscheduler.schedulers.background import BackgroundScheduler

def rotate_api_keys():
    # Lógica para generar nuevas claves y actualizar .env
    pass

scheduler = BackgroundScheduler()
scheduler.add_job(rotate_api_keys, 'interval', weeks=4)
scheduler.start()
