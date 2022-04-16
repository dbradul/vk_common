import logging

log_file = "./logfile.log"
log_level = logging.INFO
logging.basicConfig(
    level=log_level, filename=log_file, filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s"
)
logger = logging.getLogger("vk_common")
logger.addHandler(logging.StreamHandler())