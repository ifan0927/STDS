import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='Logs/InfoLog.log', filemode='a', format=FORMAT)
logger = logging.getLogger(__name__)

async def get_logger():
    return logger