import json
import os
from datetime import datetime

class WriteLosslessMemory:
    """
    WRITE_LOSSLESS: An immutable, append-only log of PION packets.
    Prevents state drift by treating memory as a ledger rather than a mutable variable.
    """
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Resolve absolute path relative to the directory where memory.py lives
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_path = os.path.join(base_dir, "chimera_memory.jsonl")
        else:
            self.storage_path = os.path.abspath(storage_path)

    def commit(self, pion_packet):
        """
        Appends a PION packet to the immutable log.
        """
        # Use a single line for each JSON object to maintain JSONL format
        if hasattr(pion_packet, 'to_json'):
            # Need to ensure to_json() doesn't use indent=2 for JSONL
            data = json.dumps(pion_packet.__dict__)
        else:
            data = json.dumps(pion_packet)
        
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(data + "\n")

    def recall_latest(self):
        """
        Retrieves the most recent PION packet from the log.
        """
        if not os.path.exists(self.storage_path):
            return None
            
        with open(self.storage_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if not lines:
                return None
            try:
                return json.loads(lines[-1])
            except json.JSONDecodeError:
                return None

    def recall_all(self):
        """
        Retrieves the entire chain of state (The Ledger).
        """
        if not os.path.exists(self.storage_path):
            return []
            
        with open(self.storage_path, "r", encoding="utf-8") as f:
            results = []
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    try:
                        results.append(json.loads(clean_line))
                    except json.JSONDecodeError:
                        continue
            return results

    def clear(self):
        """
        Danger: Resets the ledger.
        """
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
