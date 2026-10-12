from enum import Enum

class Phase(Enum):
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"

class MissionManager:
    """
    Manages phase transitions, waypoint queues, and vision task timeouts.
    """

    def __init__(self):
        # Initial State
        self.current_phase = Phase.MANUAL

    def set_phase(self, new_phase_str: str) -> bool:
        """
        Safely attempts to transition the mission state based on string input.
        Returns True if the state changed, False if ignored.
        """
        target = new_phase_str.strip().lower()
        
        if target == Phase.MANUAL.value and self.current_phase != Phase.MANUAL:
            self.current_phase = Phase.MANUAL
            return True
            
        elif target == Phase.AUTONOMOUS.value and self.current_phase != Phase.AUTONOMOUS:
            self.current_phase = Phase.AUTONOMOUS
            return True
            
        return False

    def is_autonomous(self) -> bool:
        return self.current_phase == Phase.AUTONOMOUS
