from src.hubcontroller.adapters.plc.plc_adapter import PlcAdapter

class AckPoller:
    def __init__(self, plc_adapter: PlcAdapter):
        self._plc_adapter = plc_adapter


    def poll_ack(self, db_number: int, start: int, length: int) -> bytearray:
        return self._plc_adapter.read_db(db_number, start, length)

    