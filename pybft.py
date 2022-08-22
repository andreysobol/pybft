import hashlib

from replica_state import ReplicaState
from messages import (
    commit,
    parse_title,
    parse_request,
    pre_prepare,
    parse_pre_prepare,
    prepare,
    parse_prepare,
    commit,
    parse_commit
)

def main_event_loop(replica_state, in_message, from_replica, current_time):

    def send_commit_message(replica_state):
        create_signature = "\x00" * 64

        commit_message = commit(v, n, d, replica_state.number, create_signature)

        size = replica_state.size_replica_set

        out_messages = {
            i:commit_message
            for i in range(0, size) 
            if i != replica_state.number
        }

        return out_messages

    if parse_title(in_message) == "request":
        op, t, c = parse_request(in_message)
        if replica_state.v % replica_state.size_replica_set == from_replica:

            v = replica_state.v
            n = replica_state.n
            d = hashlib.sha256(in_message).hexdigest()
            # real signtautre should be here
            signature = "\x00" * 64
            m = in_message

            pre_prepare_message = pre_prepare(v, n, d, signature, m)

            size = replica_state.size_replica_set

            out_messages = {
                i:pre_prepare_message
                for i in range(0, size) 
                if i != replica_state.number
            }

            replica_state = replica_state.copy()
            replica_state.n = n + 1
            replica_state.requests[d] = {
                "n": n,
                "pre_prepared": "sended",
                "messages": in_message,
            }
            return replica_state, out_messages
        else:
            d = hashlib.sha256(in_message).hexdigest()

            replica_state = replica_state.copy()
            replica_state.n = n + 1
            replica_state.requests[d] = {
                "n": n,
                "messages": in_message,
                "timeout": current_time + replica_state.timeout,
            }

            # mb write forwarding m to leader here

            return replica_state, {}

    
    if parse_title(in_message) == "pre_prepare":
        v, n, d, signature, m = parse_pre_prepare(in_message)

        # verfy signature here

        # verify digest here

        c1 = (replica_state.v % replica_state.size_replica_set == from_replica)
        c2 = (replica_state.v == v)
        c = c1 and c2
        if c:
            replica_state = replica_state.copy()

            # write edge case - different ordering
            # write edge case - send commit messages also

            replica_state.requests[d] = {
                "n": n,
                "pre_prepared": "recived",
                "messages": m,
            }

            create_signature = "\x00" * 64
            prepare_message = prepare(v, n, d, replica_state.number, create_signature):

            size = replica_state.size_replica_set

            out_messages = {
                i:prepare_message
                for i in range(0, size) 
                if i != replica_state.number
            }

            return replica_state, out_messages
    
    if parse_title(in_message) == "prepare":
        v, n, d, i, signature = parse_prepare(in_message)

        # verfy signature here

        # verify digest here

        c1 = (i == from_replica)
        c2 = (replica_state.v == v)
        c = c1 and c2
        if c:
            replica_state = replica_state.copy()

            if not d in replica_state.requests:
                replica_state.requests[m] = {
                    "n": n,
                    "prepared": [i],
                }
            else:
                if "prepared" not in replica_state.requests["d"]:
                    replica_state.requests["d"]["prepared"] = [i]
                else:
                    if i not in replica_state.requests["d"]["prepared"]:
                        replica_state.requests["d"]["prepared"] += [i]

                        c1 = len(replica_state.requests["d"]["prepared"]) == replica_state.size_f * 2
                        c21 = replica_state.requests["d"]["pre_prepared"] == "recived"
                        c22 = replica_state.requests["d"]["pre_prepared"] == "sended"
                        c = c1 and (c21 or c22)
                        if c:
                            out_messages = send_commit_message(replica_state)
                            return replica_state, out_messages

            return replica_state, {}
    
    if parse_title(in_message) == "commit":
        v, n, d, i, signature = parse_commit(in_message)

        # verfy signature here

        # verify digest here

        c1 = (i == from_replica)
        c2 = (replica_state.v == v)
        c = c1 and c2
        if c:
            replica_state = replica_state.copy()

            if not d in replica_state.requests:
                replica_state.requests[m] = {
                    "n": n,
                    "committed": [i],
                }
            else:
                if "committed" not in replica_state.requests["d"]:
                    replica_state.requests["d"]["committed"] = [i]
                else:
                    if i not in replica_state.requests["d"]["committed"]:
                        replica_state.requests["d"]["committed"] += [i]

                        c = len(replica_state.requests["d"]["committed"]) == replica_state.size_f * 2 + 1
                        if c:
                            out_messages = send_commit_message(replica_state)
                            return replica_state, out_messages

            return replica_state, {}

    return