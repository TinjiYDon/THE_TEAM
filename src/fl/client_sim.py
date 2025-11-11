"""
联邦学习客户端模拟（MVP骨架）：本机多客户端权重更新占位
"""
from typing import Dict, Any, List
import random


class FedClientSim:
    def __init__(self, client_id: str):
        self.client_id = client_id

    def local_train(self, base_weights: List[float], steps: int = 10) -> Dict[str, Any]:
        """
        简化：对权重做微小扰动以模拟本地训练更新
        """
        if not base_weights:
            base_weights = [0.0] * 16
        new_weights = []
        for w in base_weights:
            new_weights.append(w + random.uniform(-0.01, 0.01))
        metrics = {"loss": round(random.uniform(0.1, 0.5), 3), "auc": round(random.uniform(0.6, 0.9), 3)}
        return {"client_id": self.client_id, "weights": new_weights, "weight": 1.0, "metrics": metrics}



