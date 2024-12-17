from ina_ground_control.models.plugin.plugin_base import PluginConfigBase


class PluginServiceBase:
    def __init__(self, config:PluginConfigBase):
        self.config = config

    def search(self,value:str):
        pass
    def add(self, data:dict):
        pass
