from enum import Enum, auto

from tcod.libtcodpy import namegen_get_sets


class Policies(Enum):
    INCREASE_WAGES = auto()
    BAN_MACHINES = auto()
    RENT_DECREASE = auto()
    TITHE_DECREASE = auto()

class Policy():
    def __init__(self, type, cost, name, desc) -> None:
        self.type = type
        self.cost = cost
        self.name = name
        self.description = desc

policy_templates = {}
policy_templates[Policies.INCREASE_WAGES] = Policy(Policies.INCREASE_WAGES, 100, "Increase Wages", "Increase Wages\nCost: 100 Support")
policy_templates[Policies.BAN_MACHINES]   = Policy(Policies.BAN_MACHINES, 100,"Ban Threshing Machines", "Ban Threshing Machines\nCost: 100 Support")
policy_templates[Policies.RENT_DECREASE]  = Policy(Policies.RENT_DECREASE, 100,"Decrease Rent", "Decrease Rent\nCost: 100 Support")
policy_templates[Policies.TITHE_DECREASE] = Policy(Policies.TITHE_DECREASE, 100, "Decrease Tithes", "Decrease Tithes\nCost: 100 Support")
