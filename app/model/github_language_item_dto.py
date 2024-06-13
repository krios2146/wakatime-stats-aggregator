class GithubLanguageItemDto:
    name: str
    type: str
    color: str
    language_id: int

    def __init__(self, data: dict[str, str | int]) -> None:
        self.name = str(data.get("name", "unknown"))
        self.type = str(data.get("type", "unknown"))
        self.color = str(data.get("color", "#000000"))
        self.language_id = int(data.get("language_id", 0))
