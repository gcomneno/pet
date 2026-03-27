import json
import sys
from collections import Counter
import heapq
import zlib
from pathlib import Path

INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/reports/data/scan-2-1000000.jsonl")
OUTPUT_FILE = Path("docs/research/pet_compressed_1M.bin")
SHAPE_INDEX_FILE = Path("docs/research/pet_shape_index.json")

CHUNK_SIZE = 10000


# -------------------------
# Generatore JSONL streaming
# -------------------------
def numbers_generator():
    with INPUT_FILE.open() as f:
        for line in f:
            yield json.loads(line)


# -------------------------
# Estrazione SHAPE canonica
# -------------------------
def pet_shape(pet):

    shape = []

    for node in pet:

        if node["e"] is None:
            shape.append(None)
        else:
            shape.append(pet_shape(node["e"]))

    # canonicalizzazione (ordine irrilevante)
    shape = sorted(shape, key=str)

    return shape


# -------------------------
# Conteggio shape
# -------------------------
shape_counter = Counter()

for j in numbers_generator():

    s = str(pet_shape(j["pet"]))

    shape_counter[s] += 1


print("Shape distinte:", len(shape_counter))
print(shape_counter.most_common(20))


# -------------------------
# Huffman coding
# -------------------------
class HuffmanNode:

    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


heap = [HuffmanNode(freq, symbol) for symbol, freq in shape_counter.items()]

heapq.heapify(heap)


while len(heap) > 1:

    a = heapq.heappop(heap)
    b = heapq.heappop(heap)

    heapq.heappush(heap, HuffmanNode(a.freq + b.freq, left=a, right=b))


root = heap[0]

huffman_code = {}


def build_code(node, code=""):

    if node.symbol is not None:

        huffman_code[node.symbol] = code
        return

    build_code(node.left, code + "0")
    build_code(node.right, code + "1")


build_code(root)


# -------------------------
# Compressione streaming
# -------------------------
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

f_out = OUTPUT_FILE.open("wb")

bit_buffer = ""

count = 0


for j in numbers_generator():

    # shape
    s = str(pet_shape(j["pet"]))
    bit_buffer += huffman_code[s]

    # primi ordinati
    primes = [p["p"] for p in j["pet"]]

    prev = 0

    for p in primes:

        gap = p - prev

        bit_buffer += format(gap, "016b")

        prev = p

    count += 1

    if count % CHUNK_SIZE == 0:

        b = int(bit_buffer, 2).to_bytes((len(bit_buffer) + 7) // 8, byteorder="big")

        f_out.write(zlib.compress(b))

        bit_buffer = ""


# residuo finale
if bit_buffer:

    b = int(bit_buffer, 2).to_bytes((len(bit_buffer) + 7) // 8, byteorder="big")

    f_out.write(zlib.compress(b))


f_out.close()


# -------------------------
# Salva indice shape
# -------------------------
with SHAPE_INDEX_FILE.open("w") as f:

    json.dump(huffman_code, f, separators=(",", ":"))


print("PET-compressor prototipo completato")
print("File compresso:", OUTPUT_FILE)
print("Indice shape:", SHAPE_INDEX_FILE)
