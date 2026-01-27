from hubcontroller.domain.hub_state import HubStateSnapshot


class HubStateProvider:
    def __init__(self, hub_state: HubStateSnapshot):
        self._hub_state = hub_state


    def get_snapshot(self) -> HubStateSnapshot:
        return self._hub_state