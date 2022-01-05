
from entities.anchor import Anchor
from entities.blocker import Blocker
from entities.material import BlockMaterial, StatueMaterial

class EntityLoader():
    def __init__(self, engine) -> None:
        self.engine = engine


    def load_entity(self, entity_char, x, y, section):
        if entity_char == ord('#'):
            section.add_entity(BlockMaterial(self.engine, x, y, section))
        if entity_char == ord('S'):
            section.add_entity(StatueMaterial(self.engine, x, y, section))
        elif entity_char == ord('B'):
            section.add_entity(Blocker(self.engine, x, y))
        elif entity_char == ord('A'):
            section.add_entity(Anchor(self.engine, x, y))