__author__ = "Victor Armegioiu"

from ntheory_utilities import *

prime_cache = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 
103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 
397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499]


"""
    @param: bits
        number of bits in the prime to be generated

    @returns:
        probable prime in the given range [2 ^ (bits - 2), 2 ^ (bits - 1)]
"""
def generate_prime(bits):
    while True:
        p = random.randint(2 ** (bits - 2), 2 ** (bits - 1))
        if baillie_psw(p) and baillie_psw(2 * p  + 1):
            return 2 * p + 1


"""
    @param: n
        candidate to be tested for primality, base 2

    @returns:
        True if the candidate is not base 2-liar
        False if the number is composite
"""
def miller_rabin_base_2(n):
    d = n - 1
    s = 0

    while not d & 1: 
        d = d >> 1 
        s += 1

    x = pow(2, d, n)

    if x == 1 or x == n - 1:
        return True

    for i in range(s - 1):
        x = pow(x, 2, n) 

        if x == 1:
            return False

        elif x == n - 1:
            return True

    return False


"""
    Lucas probable prime test (pseudoprime section) as illustrated on Wikipedia.
    https://en.wikipedia.org/wiki/Lucas_pseudoprime#Lucas_probable_primes_and_pseudoprimes

    @param: n
        candidate to be tested for primality

    @param P, Q:
        Generators for the Lucas sequence 
        where Uk(P, Q) and Vk(P, Q) be the corresponding Lucas sequences.

    @param: D
        D value such that Jacobi symbol (D / n) =- 1
        details on the choosing of this value may be found
        in the baillie - PSW function description
        D = P ^ 2 - 4 * Q
"""
def lucas_pp(n, D, P, Q):                                                                                                                                                                                                                         

    U, V = U_V_subscript(n + 1, n, 1, P, P, Q, D)

    if U != 0:
        return False

    d = n + 1
    s = 0

    while not d & 1:
        d = d >> 1
        s += 1

    U, V = U_V_subscript(n + 1, n, 1, P, P, Q, D)

    if U == 0:
        return True

    for r in range(s):
        U, V = (U * V) % n, (pow(V, 2, n) - 2 * pow(Q, d * (2 ** r), n)) % n
        if V == 0:
            return True

    return False



"""
    Baillie - PSW probabilistic primality test, 
    completely deterministic for candidates below 2^64.

    Runs a sanity check through a small cache before running the Miller-Rabin
    base 2 test and the Lucas pseudoprime test.

    If the number is a perfect square, then there would be no point in trying
    to find a D s.t. (D / n) = -1 since there is no solution, hence the candidate
    is obviously a candidate.

    Other implementation details, regarding the choosing of P and Q can be found
    below.

    https://en.wikipedia.org/wiki/Baillie%E2%80%93PSW_primality_test


    @param: candidate
        candidate to be tested for primality

    @returns:
        Boolean value indicating whether the candidate is
        a probable prime or not
"""
def baillie_psw(candidate):
    for prime in prime_cache:
        if candidate == prime:
            return True
        elif candidate % prime == 0:
            return False

    if not miller_rabin_base_2(candidate):
        return False
    
    if int(sqrt(candidate) + 0.5) ** 2 == candidate:
        return False

    D = 5
    while jacobi_symbol(D, candidate) != -1:
        D += 2 if D > 0 else -2
        D *= -1
    
    if not lucas_pp(candidate, D, 1, (1 - D) / 4):
        return False

    return True
