class StateMachineOperation():

    def __init__(self, repr) -> None:
        self.op = repr
        return

    def deserialize(self, data: bytes) -> tuple:
        op_i = int.from_bytes(data, byteorder='big')
        if op_i == 0:
            return (0, 0)
        if op_i == 1:
            return (0, 1)
        if op_i == 2:
            return (1, 0)
        if op_i == 3:
            return (1, 1)

    def serialize(self) -> bytes:
        if self.op == (0, 0):
            return (0).to_bytes(1, byteorder='big')
        if self.op == (0, 1):
            return (1).to_bytes(1, byteorder='big')
        if self.op == (1, 0):
            return (2).to_bytes(1, byteorder='big')
        if self.op == (1, 1):
            return (3).to_bytes(1, byteorder='big')