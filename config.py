from ruamel.yaml import YAML

class AppConfig():
    def __init__(self):
        with open("config/config.yml","r",encoding="utf-8") as configFile:
            yaml = YAML()
            conf = yaml.load(configFile)
            self.config = conf
            self.loguru = self.config['loguru']
            self.uvicorn = self.config['uvicorn']

        
appConfig = AppConfig()
