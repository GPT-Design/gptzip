import os
import hashlib
import json
import zlib
from bloom_filter2 import BloomFilter
from anytree import Node
from datetime import datetime

class GPTZip:
    def __init__(self, storage_path="gptzip_storage"):
        self.storage_path = storage_path
        self.index_file = os.path.join(storage_path, "index.json")
        self.bloom_filter = BloomFilter(max_elements=1000000, error_rate=0.01)
        self.index = {}
        os.makedirs(storage_path, exist_ok=True)
        self._load_index()

    def _hash_data(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def _compress_data(self, data):
        return zlib.compress(data.encode())

    def _decompress_data(self, compressed_data):
        return zlib.decompress(compressed_data).decode()

    def _load_index(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, "r") as f:
                self.index = json.load(f)
                for key in self.index.keys():
                    self.bloom_filter.add(key)

    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=4)

    def compress(self, data):
        data_hash = self._hash_data(data)
        if data_hash in self.bloom_filter:
            return f"Entry already exists: {data_hash}"
        compressed_data = self._compress_data(data)
        file_path = os.path.join(self.storage_path, f"{data_hash}.gz")
        with open(file_path, "wb") as f:
            f.write(compressed_data)
        self.index[data_hash] = {"timestamp": str(datetime.utcnow()), "size": len(compressed_data)}
        self.bloom_filter.add(data_hash)
        self._save_index()
        return f"Data compressed successfully: {data_hash}"

    def decompress(self, data_hash):
        if data_hash not in self.index:
            return "Entry not found."
        file_path = os.path.join(self.storage_path, f"{data_hash}.gz")
        with open(file_path, "rb") as f:
            compressed_data = f.read()
        return self._decompress_data(compressed_data)

    def list_entries(self):
        return list(self.index.keys()) if self.index else "No entries stored."

if __name__ == "__main__":
    gptzip = GPTZip()
    print("GPTZip v3.0 initialized.")
