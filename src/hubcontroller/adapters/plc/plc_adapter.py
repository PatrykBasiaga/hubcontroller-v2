import snap7

class PlcAdapter:
    def __init__(self, plc_ip: str, rack: int, slot: int, tcp_port: int):
        self._plc_ip = plc_ip
        self._rack = rack
        self._slot = slot
        self._tcp_port = tcp_port
        self.client_read = None
        self.client_write = None

    def connect_read(self):
        try:
            if self.client_read is not None and not self.is_connected_read():
                self.disconnect_read()
            
            if self.client_read is None:
                self.client_read = snap7.client.Client()
                self.client_read.connect(address=self._plc_ip, rack=self._rack, slot=self._slot, tcp_port=self._tcp_port)
        except Exception as e:
            self.disconnect_read()
            raise


    def connect_write(self):
        try:
            if self.client_write is not None and not self.is_connected_write():
                self.disconnect_write()
            
            if self.client_write is None:
                self.client_write = snap7.client.Client()
                self.client_write.connect(address=self._plc_ip, rack=self._rack, slot=self._slot, tcp_port=self._tcp_port)
        except Exception as e:
            self.disconnect_write()
            raise

    def connect_clients(self):
        self.connect_read()
        self.connect_write()

    def is_connected_read(self) -> bool:
        if self.client_read is None:
            return False
        return self.get_plc_state(self.client_read) == 'S7CpuStatusRun'

    def is_connected_write(self) -> bool:
        if self.client_write is None:
            return False
        return self.get_plc_state(self.client_write) == 'S7CpuStatusRun'

    def get_plc_state(self, client: snap7.client.Client) -> str | None:
        try:
            state = client.get_cpu_state()
        except Exception as e:
            return None
        return snap7.types.cpu_statuses.get(state)

    def disconnect_write(self):
        try:
            if self.client_write is not None:
                self.client_write.disconnect()
                self.client_write.destroy()
                self.client_write = None

        except Exception as e:
            if self.client_write is not None: 
                self.client_write.destroy()
                self.client_write = None


    def disconnect_read(self):
        try:
            if self.client_read is not None:
                self.client_read.disconnect()
                self.client_read.destroy()
                self.client_read = None
        except Exception as e:
            if self.client_read is not None: 
                self.client_read.destroy()
                self.client_read = None

    def read_db(self, db_number: int, start: int, length: int) -> bytes:
        try:
            self.ensure_connected_read()
            return self.client_read.db_read(db_number, start, length)
        except Exception as e:
            self.disconnect_read()
            raise

    def write_db(self, db_number: int, start: int, data: bytes) -> None:
        try:
            self.ensure_connected_write()
            self.client_write.db_write(db_number, start, data)
        except Exception as e:
            self.disconnect_write()     
            raise

    def ensure_connected_read(self) -> None:
        if self.client_read is None or not self.is_connected_read():
            self.connect_read()
    
    def ensure_connected_write(self) -> None:
        if self.client_write is None or not self.is_connected_write():
            self.connect_write()