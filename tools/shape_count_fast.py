import math

PRIMES = [
2,3,5,7,11,13,17,19,23,29,
31,37,41,43,47
]

# memo per evitare ricalcoli
shape_cache = {}

def shape_exp(e):
    """
    Shape PET dell'intero e (solo per esponenti)
    """
    if e == 1:
        return None

    if e in shape_cache:
        return shape_cache[e]

    factors = []
    x = e
    p = 2

    while p*p <= x:
        count = 0
        while x % p == 0:
            x //= p
            count += 1
        if count:
            factors.append(shape_exp(count))
        p += 1

    if x > 1:
        factors.append(None)

    s = tuple(sorted(factors, key=str))
    shape_cache[e] = s
    return s


def count_shapes(N):

    shapes = set()

    def dfs(i, last_exp, current_n, exps):

        if current_n > N:
            return

        if exps:
            shape = tuple(sorted((shape_exp(e) for e in exps), key=str))
            shapes.add(shape)

        if i >= len(PRIMES):
            return

        p = PRIMES[i]

        for e in range(last_exp, 0, -1):

            new_n = current_n * (p ** e)

            if new_n > N:
                continue

            dfs(i+1, e, new_n, exps + [e])

    dfs(0, 60, 1, [])

    return len(shapes)


targets = [
10**6,
10**7,
10**8,
10**9,
10**10,
10**11,
10**12,
10**13,
10**14,
10**15,
10**16,
10**17,
10**18,
10**19,
10**20,
10**21,
10**22,
10**23,
10**24,
]

for N in targets:
    print(N, count_shapes(N))
