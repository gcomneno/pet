import math
import matplotlib.pyplot as plt

data = [
(10**6,78),
(10**7,109),
(10**8,146),
(10**9,191),
(10**10,250),
(10**11,321),
(10**12,400),
(10**13,499),
(10**14,614),
(10**15,751),
(10**16,904),
(10**17,1087),
(10**18,1291),
(10**19,1528),
(10**20,1803),
(10**21,2096),
(10**22,2441),
(10**23,2808),
(10**24,3223)
]

x=[]
y=[]

for N,S in data:
    x.append((math.log(N))**2)
    y.append(S)

plt.figure()

plt.scatter(x,y)

plt.xlabel("(log N)^2")
plt.ylabel("S(N)")
plt.title("Growth law of PET structural space")

plt.grid(True)

plt.savefig("artifacts/pet_shape_growth_law.png",dpi=300)

plt.show()
