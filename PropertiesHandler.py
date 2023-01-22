import configparser as cp


class PropertiesHandler:
    def __init__(self):
        self.config = cp.ConfigParser()
        self.config.read('properties.ini')

    def get_services(self):
        return self.config['TAGS']['Services']

    def get_default_id(self):
        return self.config['TAGS']['Default_Id']

    def get_main(self):
        return self.config['ADDRESSES']['Main']

    def get_data(self):
        return self.config['ADDRESSES']['Data']

    def get_red(self):
        return self.config['TAGS']['Red']
