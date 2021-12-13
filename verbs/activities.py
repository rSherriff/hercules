from enum import Enum, auto

class Activities(Enum):
    BREAKING = auto()
    ARSON = auto()
    LETTER = auto()
    MEETING = auto()
    ROBBERY = auto()

class Activity():
    def __init__(self, type, power, support, threat, name, desc) -> None:
        self.type = type
        self.power = power
        self.support = support
        self.name = name
        self.threat_generated = threat
        self.description = desc


activity_templates = {}
activity_templates[Activities.BREAKING] = Activity(Activities.BREAKING, 10,10,100,"Machine Breaking", "Break Threshing Machine\n10 Power\n10Support")
activity_templates[Activities.ARSON]   = Activity(Activities.ARSON, 20, -30,100,"Arson", "Arson\n20 Power\n-30Support")
activity_templates[Activities.LETTER]  = Activity(Activities.LETTER, 20, -10,100,"Swing Letter", "Swing Letter\n20 Power\n-10Support")
activity_templates[Activities.MEETING] = Activity(Activities.MEETING, -10, 20,100,"Meeting", "Meeting\n-10 Power\n20Support")
activity_templates[Activities.ROBBERY] = Activity(Activities.ROBBERY, 10, -10,100,"\"Robbery\"","\"Robbery\"\n10 Power\n-10Support")