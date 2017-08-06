import random, json, sys
# Represent K as an array abcdefghijklmnop of 16 integers meaning a*K[0] + b*K[1] + c*K[2]
K = []
f = [1] + [0] * 15

# Initialize with 1000000000000000 meaning 1*K[0], 0100000000000000 meaning 0*K[0]+1*K[1]
# etc
for x in range(16):
    K.append(f)
    f = [f[15]] + f[:15]

def galoisMult(a, b):
    p = 0
    hiBitSet = 0
    for i in range(8):
        if b & 1 == 1:
            p ^= a
        hiBitSet = a & 0x80
        a <<= 1
        if hiBitSet == 0x80:
            a ^= 0x1b
        b >>= 1
    return p % 256

def xor(a1,a2):
    return [x ^ y for (x,y) in zip(a1,a2)]

# Show an entry in K as an equation
def val2eqn(f):
    return '+ '.join(["%s*K[%s]" % (f[x],x) for x in range(16) if f[x] != 0])

# Clock function that works with equations
def clock2():
    new = xor(K[6],K[9])
    k = [galoisMult(119,x) for x in K[15]]
    new = xor(new,k)
    i = 15
    while i > 0:
        K[i] = K[i-1]
        i -= 1
    K[0] = new

for x in range(8192):
    clock2()
    print "%s: i=%s j=%s" % (x, val2eqn(K[4]), val2eqn(K[10]))
