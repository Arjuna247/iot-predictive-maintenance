import hashlib, json, time

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), time.time(), data, latest_block.hash)
        self.chain.append(new_block)

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index} | Hash: {block.hash} | Data: {block.data}")

    def save_chain(self, filename="ledger.json"):
        with open(filename, "w") as f:
            json.dump([{
                "index": b.index,
                "timestamp": b.timestamp,
                "data": b.data,
                "previous_hash": b.previous_hash,
                "hash": b.hash
            } for b in self.chain], f, indent=4)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                print(f"❌ Block {i} has been tampered!")
                return False

            if current.previous_hash != prev.hash:
                print(f"❌ Block {i} has wrong previous hash link!")
                return False

        print("✅ Blockchain is valid and secure.")
        return True
