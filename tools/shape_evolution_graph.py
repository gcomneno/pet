import math

PRIMES = [2,3,5,7,11,13,17,19,23,29,31]

shape_cache = {}

def shape_exp(e):
    if e == 1:
        return None

    if e in shape_cache:
        return shape_cache[e]

    x = e
    p = 2
    factors = []

    while p*p <= x:
        c = 0
        while x % p == 0:
            x//=p
            c+=1
        if c:
            factors.append(shape_exp(c))
        p+=1

    if x>1:
        factors.append(None)

    s = tuple(sorted(factors,key=str))
    shape_cache[e]=s
    return s


def depth(shape):
    if shape is None:
        return 0
    if not shape:
        return 1
    return 1 + max(depth(s) for s in shape)


def enumerate_shapes(N):

    shapes = {}
    edges = set()

    def dfs(i,last_exp,current_n,exps):

        if current_n>N:
            return

        if exps:
            shape = tuple(sorted((shape_exp(e) for e in exps),key=str))

            if shape not in shapes:
                shapes[shape]=current_n

                parent = exps[:-1]

                if parent:
                    parent_shape = tuple(sorted((shape_exp(e) for e in parent),key=str))
                    edges.add((parent_shape,shape))

        if i>=len(PRIMES):
            return

        p=PRIMES[i]

        for e in range(last_exp,0,-1):

            new_n=current_n*(p**e)

            if new_n>N:
                continue

            dfs(i+1,e,new_n,exps+[e])

    dfs(0,60,1,[])

    return shapes,edges


N = 10**12

shapes,edges = enumerate_shapes(N)

with open("artifacts/pet_shape_evolution.dot","w") as f:

    f.write("digraph PET {\n")

    for s,n in shapes.items():

        d = depth(s)

        colors = [
            "#fee8c8",
            "#fdbb84",
            "#fc8d59",
            "#ef6548",
            "#d7301f",
            "#990000"
        ]

        c = colors[min(d,len(colors)-1)]

        f.write(
            f'"{s}" '
            f'[label="{n}", style=filled, fillcolor="{c}"];\n'
        )

    for a,b in edges:
        f.write(f'"{a}" -> "{b}";\n')

    f.write("}\n")

print("graph written to artifacts/pet_shape_evolution.dot")
