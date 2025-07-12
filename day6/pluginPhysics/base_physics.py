from abc import ABC, abstractmethod

class BasePhysicsEngine(ABC):
    @abstractmethod
    def create_body(self, x, y, w, h, **kwargs):
        pass

    @abstractmethod
    def remove_body(self, bid):
        pass

    @abstractmethod
    def get_body(self, bid):
        pass

    @abstractmethod
    def apply_force(self, bid, fx, fy):
        pass

    @abstractmethod
    def update(self, dt):
        pass 