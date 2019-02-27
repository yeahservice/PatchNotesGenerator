class Patch():
    
    def __init__(self, version):
        self.version = version
        self.summary = ""
        self.champions = {}
        
    def add_champion(self, champion):
        self.champions[champion.name] = champion


class Champion():
    
    def __init__(self, name):
        self.name = name
        self.summary = ""
        self.description = ""


def serialize(obj):
    if isinstance(obj, Patch) or isinstance(obj, Champion):
        return obj.__dict__
    else:
        raise TypeError ("Type not serializable")