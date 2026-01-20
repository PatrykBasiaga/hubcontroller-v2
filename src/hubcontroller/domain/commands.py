from enum import Enum
from dataclasses import dataclass


@dataclass#(frozen=True)
class Command:
    command_id: str
    command_type: str
    payload: dict
     

class CommmandStatus(Enum):
    ACCEPTED = "accepted" 


cts = Command(command_id="123", command_type="test", payload={"test": "test"})
cts.command_idsssss = "456"
print(cts.__dict__)
