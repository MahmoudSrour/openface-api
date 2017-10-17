import requests


class Users:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def get(self, subject_id):
        method = "users::get"
        self.logger.info("Calling {0} method".format(method))

        url = "{0}/api/users/{1}".format(self.config.api['users-gallery-host'], subject_id)
        self.logger.info("Start calling get user api, url {0}".format(url))
        resp = requests.get(url).json()
        self.logger.info("End calling get user api, result {0}".format(resp['ImagePath']))
        return resp


    def post(self):
        print("To be implemeted")
