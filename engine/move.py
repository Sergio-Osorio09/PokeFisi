class Move:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.type = data["type"]
        self.base_power = data["base_power"]
        self.accuracy = data["accuracy"]
        self.category = data["category"]
        self.effect = data.get("effect", "none")

    def __repr__(self):
        return f"Move({self.name}, {self.type}, BP:{self.base_power})"
