class ReplicaState():

    def __init__(self, replica_number, v, n, requests) -> None:
        self.replica_number = replica_number
        self.v = v
        self.n = n
        self.requests = requests
        self.size_replica_set = 10
        self.size_f = 3

    def copy(self) -> 'ReplicaState':
        requests = self.requests.copy()
        return ReplicaState(
            self.replica_number,
            self.v,
            self.n,
            requests
        )