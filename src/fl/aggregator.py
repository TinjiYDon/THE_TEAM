"""
联邦学习聚合器（MVP骨架）
"""
from typing import List, Dict, Any
import hashlib
import json
import sqlite3

try:
    from ..config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


class FedAggregator:
    def __init__(self):
        pass

    def fedavg(self, client_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        简化版FedAvg：假设每个客户端提交相同维度的权重向量weights: List[float]
        """
        if not client_updates:
            return {"weights": []}
        dim = len(client_updates[0]["weights"])
        agg = [0.0] * dim
        total_w = 0.0
        for upd in client_updates:
            w = float(upd.get("weight", 1.0))
            total_w += w
            ws = upd["weights"]
            for i in range(dim):
                agg[i] += ws[i] * w
        if total_w > 0:
            agg = [x / total_w for x in agg]
        return {"weights": agg}

    def save_model_version(self, weights: List[float], metrics: Dict[str, Any], active: int = 0) -> int:
        s = json.dumps(weights, sort_keys=True)
        h = hashlib.sha256(s.encode("utf-8")).hexdigest()
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO fl_model_versions (model_hash, metrics, active, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (h, json.dumps(metrics, ensure_ascii=False), active))
        conn.commit()
        conn.close()
        return 1


fed_aggregator = FedAggregator()

