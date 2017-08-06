import random, json, sys
K = []
f = [1] + [0] * 15
for x in range(16):
    K.append(f)
    f = [f[15]] + f[:15]

T = [0x00,0x77,0xee,0x99,0xc7,0xb0,0x29,0x5e,0x95,0xe2,0x7b,0x0c,0x52,0x25,0xbc,0xcb,0x31,0x46,0xdf,0xa8,0xf6,0x81,0x18,0x6f,0xa4,0xd3,0x4a,0x3d,0x63,0x14,0x8d,0xfa,0x62,0x15,0x8c,0xfb,0xa5,0xd2,0x4b,0x3c,0xf7,0x80,0x19,0x6e,0x30,0x47,0xde,0xa9,0x53,0x24,0xbd,0xca,0x94,0xe3,0x7a,0x0d,0xc6,0xb1,0x28,0x5f,0x01,0x76,0xef,0x98,0xc4,0xb3,0x2a,0x5d,0x03,0x74,0xed,0x9a,0x51,0x26,0xbf,0xc8,0x96,0xe1,0x78,0x0f,0xf5,0x82,0x1b,0x6c,0x32,0x45,0xdc,0xab,0x60,0x17,0x8e,0xf9,0xa7,0xd0,0x49,0x3e,0xa6,0xd1,0x48,0x3f,0x61,0x16,0x8f,0xf8,0x33,0x44,0xdd,0xaa,0xf4,0x83,0x1a,0x6d,0x97,0xe0,0x79,0x0e,0x50,0x27,0xbe,0xc9,0x02,0x75,0xec,0x9b,0xc5,0xb2,0x2b,0x5c,0x93,0xe4,0x7d,0x0a,0x54,0x23,0xba,0xcd,0x06,0x71,0xe8,0x9f,0xc1,0xb6,0x2f,0x58,0xa2,0xd5,0x4c,0x3b,0x65,0x12,0x8b,0xfc,0x37,0x40,0xd9,0xae,0xf0,0x87,0x1e,0x69,0xf1,0x86,0x1f,0x68,0x36,0x41,0xd8,0xaf,0x64,0x13,0x8a,0xfd,0xa3,0xd4,0x4d,0x3a,0xc0,0xb7,0x2e,0x59,0x07,0x70,0xe9,0x9e,0x55,0x22,0xbb,0xcc,0x92,0xe5,0x7c,0x0b,0x57,0x20,0xb9,0xce,0x90,0xe7,0x7e,0x09,0xc2,0xb5,0x2c,0x5b,0x05,0x72,0xeb,0x9c,0x66,0x11,0x88,0xff,0xa1,0xd6,0x4f,0x38,0xf3,0x84,0x1d,0x6a,0x34,0x43,0xda,0xad,0x35,0x42,0xdb,0xac,0xf2,0x85,0x1c,0x6b,0xa0,0xd7,0x4e,0x39,0x67,0x10,0x89,0xfe,0x04,0x73,0xea,0x9d,0xc3,0xb4,0x2d,0x5a,0x91,0xe6,0x7f,0x08,0x56,0x21,0xb8,0xcf]

# XOR a with b as key, rotate over b if needed
def string_xor(a,key):
        return ''.join(chr(ord(a[i]) ^ ord(key[i%len(key)])) for i in range(len(a)))

# Plain RC4 setup with a random 16 byte key K
def setup():
    global K
    global S
    S = [i for i in range(256)]
    j = 0
    for i in range(256):
        j = (K[i % len(K)] + S[i] + j) % 256
        S[i], S[j] = S[j], S[i]

# Rotate K and do an XOR + T lookup for new K[0]
def clock():
    new = K[6] ^ T[K[15]] ^ K[9] # GF: K[6] + K[9] + 119*K[15]
    i = 15
    while i > 0:
        K[i] = K[i-1]
        i -= 1
    K[0] = new

def get_random(count,output):
    setup()
    global K
    i = 0
    j = 0
    for idx in range(count):
        clock()
        i = K[4]  # normal RC4 i = (i + 1)    % 256
        j = K[10] # normal RC4 j = (j + S[i]) % 256
        output[idx] = chr(S[(S[j] + S[i]) % 256])
        S[i], S[j] = S[j], S[i]

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

def clock2():
    new = xor(K[6],K[9])
    k = [galoisMult(119,x) for x in K[15]]
    new = xor(new,k)
    i = 15
    while i > 0:
        K[i] = K[i-1]
        i -= 1
    K[0] = new

def gdiv(a,b):
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    for x in range(256):
        if galoisMult(b,x) == a:
            return x

# Solve a table of equations, modified to work in GF
# modified from https://martin-thoma.com/solving-linear-equations-with-gaussian-elimination/
def gauss(A):
    n = len(A)
    for i in range(0, n):
        # Make all rows below this one 0 in current column
        for k in range(i+1, n):
            c = gdiv(A[k][i],A[i][i])
            for j in range(i, n+1):
                A[k][j] ^= galoisMult(c,A[i][j])

    # Solve equation Ax=b for an upper triangular matrix A
    x = [0 for i in range(n)]
    for i in range(n-1, -1, -1):
        x[i] = gdiv(A[i][n],A[i][i])
        for k in range(i-1, -1, -1):
            A[k][n] ^= galoisMult(A[k][i], x[i])
    return x


# For speed, cache the ival and jval table
testsize = 8192
ival = []
jval = []
for x in range(testsize):
    clock2()
    ival.append(K[4])
    jval.append(K[10])

f = open(sys.argv[1]).read(testsize)
tot = []
for c in range(len(f)-6):
    if f[c] == f[c+6]:
        # At distance 6 j is what i was 6 steps before
        # if the same character occurs at this distance then there is a good chance that
        # what is now i is the same as j was before so we have an equation 
        # like X[1]^58*X[2] .. == 22*X[0]+17*x[1]...
        e = xor(jval[c],ival[c+6]) # xor left and right together = 0
        e = xor(e,[1]+[0]*15) # now XOR in 1*K[0] so now we have an equation like K[0] = 22*X[0]^X[1]....
        tot.append(e)

orig2 = tot
# Take a random set of the equations since there might be false positives
while True:
    print "Checking solution..."
    orig = orig2
    tot = []
    # Pick 16 random equations from the list
    while len(tot) < 16:
        i = random.randint(0,len(orig)-1)
        tot.append(orig[i])
        orig = orig[:i] + orig[i+1:]

    test_val = f[128:256]
    # Now make a guess for K[0] and try to solve the equations
    for guess in range(0,256):
        n = 16
        A = [[0 for j in range(n+1)] for i in range(n)]
        i = 0
        for d in tot:
            A[i] = d + [guess]
            i += 1
        # Calculate solution
        try:
            x = gauss(A)
        except ZeroDivisionError:
            continue
        # Generate random bytes using the guessed key and see if they match the original file
        K = x[:]
        setup()
        out = [0] * 256
        get_random(256,out)
        if ''.join(out[128:256]) == test_val:
            print "FOUND KEY: %s" % x
            K = x[:]
            data = open(sys.argv[1]).read()
            out = [0] * 8192
            setup()
            get_random(8192,out)
            out = ''.join(out)
            print string_xor(out,data)
            exit()
