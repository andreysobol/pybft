from state_machine import StateMachineOperation

def serialize_title(data):
    first = data.encode('utf-8')
    increase = 16 - len(first)
    second = b'\x00' * increase
    return first + second 

def deserialize_title(blob):
    pre =  blob[:16].decode('utf-8')
    return pre.split('\x00')[0]

def parse_title(message):
    return deserialize_title(message[:16])

# o - state machine operation or state transition in other word
# t - timestamp
# c - client id
def request(o, t, c):
    title = serialize_title("request")
    return title + o.serialize() + t.to_bytes(8, byteorder='big') + c.to_bytes(8, byteorder='big')

def parse_request(message) -> tuple:
    return (
        StateMachineOperation.deserialize(message[16:20]),
        int.from_bytes(message[20:28], byteorder='big'),
        int.from_bytes(message[28:36], byteorder='big'),
    )

# v - view number
# n - sequence number
# d - digest for message m
# signature
# m - message, request
def pre_prepare(v, n, d, signature, m):
    title = serialize_title("pre_prepare")
    sv = v.to_bytes(8, byteorder='big')
    sn = n.to_bytes(8, byteorder='big')
    sd = d
    # 64 bytes for signature
    ssignature = signature
    sm = m
    return title + sv + sn + sd + ssignature + sm

def parse_pre_prepare(message) -> tuple:
    return (
        int.from_bytes(message[16:24], byteorder='big'),
        int.from_bytes(message[24:32], byteorder='big'),
        message[32:64],
        message[64:128],
        parse_request(message[48:])
    )


# v - view number
# n - sequence number
# d - digest for message m
# i - replica id
# signature
def prepare(v, n, d, i, signature):
    title = serialize_title("prepare")
    sv = v.to_bytes(8, byteorder='big')
    sn = n.to_bytes(8, byteorder='big')
    sd = d
    si = i.to_bytes(8, byteorder='big')
    # 64 bytes for signature
    ssignature = signature
    return title + sv + sn + sd + si + ssignature

def parse_prepare(message) -> tuple:
    return (
        int.from_bytes(message[16:24], byteorder='big'),
        int.from_bytes(message[24:32], byteorder='big'),
        message[32:64],
        int.from_bytes(message[64:72], byteorder='big'),
        message[72:136],
    )


# v - view number
# n - sequence number
# d - digest for message m
# i - replica id
# signature
def commit(v, n, d, i, signature):
    title = serialize_title("prepare")
    sv = v.to_bytes(8, byteorder='big')
    sn = n.to_bytes(8, byteorder='big')
    sd = d
    si = i.to_bytes(8, byteorder='big')
    # 64 bytes for signature
    ssignature = signature
    return title + sv + sn + sd + si + ssignature

def parse_commit(message) -> tuple:
    return (
        int.from_bytes(message[16:24], byteorder='big'),
        int.from_bytes(message[24:32], byteorder='big'),
        message[32:64],
        int.from_bytes(message[64:72], byteorder='big'),
        message[72:136],
    )

def chekpoint(n, d, i, signature):
    title = serialize_title("checkpoint")
    sn = n.to_bytes(8, byteorder='big')
    sd = d
    si = i.to_bytes(8, byteorder='big')
    # 64 bytes for signature
    ssignature = signature
    return title + sn + sd + si + ssignature

def parse_checkpoint(message) -> tuple:
    return (
        int.from_bytes(message[16:24], byteorder='big'),
        message[24:56],
        int.from_bytes(message[56:64], byteorder='big'),
        message[64:128],
    )

# uncomment it after checkpoint implementation

#def view_change(v, n, ):
#    title = serialize_title("view_change")
#    return title