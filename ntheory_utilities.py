__author__ = "Victor Armegioiu"

from math import sqrt
import random

"""
    @param: base 
        base to be used for modular exponentiation

    @param: exp
        power to raise the base to

    @param: modulo
        value of the field we're working in, (Z/pZ)*

    @returns: 
        Computes (base ^ exp) % modulo in log2(exp) time.
"""
def mod_exp(base, exp, modulo):
    ans = 1
    while exp:
        if exp & 1:
            ans = (ans * base) % modulo

        base = (base * base) % modulo
        exp >>= 1

    return ans

"""
    Computation of the Jacobi symbol (a / n) using modular congruences.
    Calculated using the properties listed here :
    https://en.wikipedia.org/wiki/Jacobi_symbol#Calculating_the_Jacobi_symbol   

    @param: a
        numerator of the jacobi symbol

    @param: b
        denominator of the jacobi symbol

    @returns:
        value of the jacobi symbol (a / n)
"""
def jacobi_symbol(a, n):
    if n == 1:
        return 1

    elif a == 0:
        return 0

    elif a == 1:
        return 1

    elif a == 2:
        if n % 8 in [3, 5]:
            return -1
        elif n % 8 in [1, 7]:
            return 1

    elif a < 0:
        return (-1) ** ((n - 1) / 2) * jacobi_symbol(-1 * a, n)

    if a % 2 == 0:
        return jacobi_symbol(2, n) * jacobi_symbol(a / 2, n)

    elif a % n != a:
        return jacobi_symbol(a % n, n)

    else:
        if a % 4 == n % 4 == 3:
            return -1 * jacobi_symbol(n, a)
        else:
            return jacobi_symbol(n, a)


"""
    @param: p
        p is a prime s.t. p = 2 * q + 1 and q == prime
        As such, the only prime divisors of p - 1 are
        2 and (p - 1) / 2 = q;

    @returns:
        primitive root of the prime p iff p = 2 * q + 1
"""
def primitive_root(p):
    s = p - 1
    divisors = (2, s // 2)

    while True:
        g = random.randint(2, p - 1)
        if mod_exp(g, s // divisors[0], p) != 1 and mod_exp(g, s // divisors[1], p) != 1:
            return g

"""
    Quick computation of the U_{n + 1} and V_{n + 1} without
    calculating intermediate terms.

    https://en.wikipedia.org/wiki/Lucas_pseudoprime#Implementing_a_Lucas_probable_prime_test
"""
def U_V_subscript(k, n, U, V, P, Q, D):
    k, n, U, V, P, Q, D = map(int, (k, n, U, V, P, Q, D))
    digits = list(map(int, str(bin(k))[2 : ]))
    subscript = 1

    for digit in digits[1 : ]:
        U, V = U * V  % n, (pow(V, 2, n) - 2 * pow(Q, subscript, n)) % n
        subscript *= 2

        if digit == 1:
            if not (P * U + V) & 1:
                if not (D * U + P * V) & 1:
                    U, V = (P * U + V) >> 1, (D * U + P * V) >> 1

                else:
                    U, V = (P * U + V) >> 1, (D * U + P * V + n) >> 1

            elif not (D * U + P * V) & 1:
                U, V = (P * U + V + n) >> 1, (D * U + P * V) >> 1

            else:
                U, V = (P * U + V + n) >> 1, (D * U + P * V + n) >> 1

            subscript += 1
            U, V = U % n, V % n

    return U, V


def encode(plaintext, bits):
	byte_array = bytearray(plaintext, 'utf-16')
	encoded = []

	chunk = bits // 8
	j = -chunk

	for i in range(len(byte_array)):
		if i % chunk == 0:
			j += chunk
			encoded.append(0)

		encoded[j // chunk] += byte_array[i] * (2 ** (8 * (i % chunk)))

	return encoded


def decode(encoded, bits):
	byte_array = []
	chunk = bits // 8

	for integer in encoded:
		for i in range(chunk):
			copy = integer

			for j in range(i + 1, chunk):
				copy %= 2 ** (8 * j)

			letter = copy // (2 ** (8 * i))
			byte_array.append(letter)
		
			integer -= letter * 2 ** (8 * i)


	decoded = bytearray(b for b in byte_array).decode('utf-16')
	return decoded
