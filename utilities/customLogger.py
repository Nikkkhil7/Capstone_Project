import logging
import os

class LogGen:
    @staticmethod
    def loggen():
        log_path = "./logs"
        os.makedirs(log_path, exist_ok=True)  # ✅ Create folder if missing

        logging.basicConfig(
            filename=os.path.join(log_path, "automation.log"),
            format='%(asctime)s: %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO
        )
        logger = logging.getLogger()
        return logger
