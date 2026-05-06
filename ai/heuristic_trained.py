import json
import glob
import os
from ai.heuristic_advanced import HeuristicAdvancedAgent


class HeuristicTrainedAgent(HeuristicAdvancedAgent):
    def __init__(self, weights_file: str):
        with open(weights_file) as f:
            data = json.load(f)
        super().__init__(weights=data["weights"])
        self.name = f"HeuristicaAvanzada-{data['battles']}"
        self.battles_trained = data["battles"]
        self.win_rate_training = data.get("win_rate", 0.0)


def find_trained_weights() -> list[str]:
    base = os.path.join(os.path.dirname(__file__), '..', 'data')

    def _battle_count(p: str) -> int:
        try:
            return int(os.path.basename(p).replace('weights_', '').replace('.json', ''))
        except ValueError:
            return 0

    return sorted(glob.glob(os.path.join(base, 'weights_*.json')), key=_battle_count)
