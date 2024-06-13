from uuid import UUID


class Chart:
    uuid: UUID
    path: str

    def __init__(self, uuid: UUID, path: str):
        self.uuid = uuid
        self.path = path
