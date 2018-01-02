from ntheory_utilities import * 
from primality_tests import generate_prime

"""
	KeyGenerator object; generates a key description based on the
	multplicative field described by a random 'bits' sized prime.

	Requires the number of bits wanted.

	'p' - prime for the field (Z/pZ)* (p is of the form 2 * q + 1 where q == prime)
	'g' - generator for this field
	'x' - private key, chosen randomly from this group {1... ord(g) - 1} 
	      where ord(g) = totient(2 * q + 1) = 2 * q
	'h' - g ^ x, to be used for encryption (finding 'x' is hard, because of
											the discrete logarithm problem)
"""

class KeyGenerator:
	def __init__(self, bits):
		self.bits = bits
		
		self.p = generate_prime(bits)
		self.g = primitive_root(self.p)
		
		self.x = random.randint(1, self.p - 2)
		self.h = mod_exp(self.g, self.x, self.p)

	def get_public_key(self):
		return {'PRIME' : self.p, 'GENERATOR' : self.g, 'H' : self.h, 'BITS' : self.bits}

	def get_private_key(self):
		return {'PRIME' : self.p, 'GENERATOR' : self.g, 'X' : self.x, 'BITS' : self.bits}

"""
	ElGamal encryption object; requires a keygenerator object and
	plaintext string to be encrypted. Both the encryption and decryption
	algorithms follow the procedure described in the article below:

	https://en.wikipedia.org/wiki/ElGamal_encryption
"""

class ElGamal:
	def __init__(self, key_gen, text, mode):
		self.key_gen = key_gen
		self.public_key = key_gen.get_public_key()
		self.private_key = key_gen.get_private_key()

		if mode == 'encrypt':
			self.plain_text = text
			self.cipher_text = None

		if mode == 'decrypt':
			self.plain_text = None
			self.cipher_text = text

		self.bits = key_gen.bits

	def update_parameters(key_gen=None, plain_text=None):
		if key_gen:
			self.key_gen = key_gen
			self.public_key = key_gen.get_public_key()
			self.private_key = key_gen.get_private_key()
			self.buts = key_gen.bits

		if plain_text:
			self.plain_text = plain_text

		self.ciphertext = None

	def encrypt(self):
		p = self.public_key['PRIME']
		g = self.public_key['GENERATOR']
		h = self.public_key['H']
		bits = self.public_key['BITS']

		encoded = encode(self.plain_text, self.bits)
		encrypted_pairs = []

		for integer in encoded:
			y = random.randint(0, p)

			c1 = mod_exp(g, y, p)
			c2 = (integer * mod_exp(h, y, p)) % p

			encrypted_pairs.append((c1, c2))

		encrypted_str = ''
		for cypher_pair in encrypted_pairs:
			encrypted_str += str(cypher_pair[0]) + ' ' + str(cypher_pair[1]) + ' '

		self.cipher_text = encrypted_str
		return encrypted_str

	def decrypt(self):
		p = self.private_key['PRIME']
		g = self.private_key['GENERATOR']
		x = self.private_key['X']
		bits = self.private_key['BITS']

		decrypted_text = []
		cipher_text = self.cipher_text.split()

		if len(cipher_text) & 1:
			return 'Malformed Cipher Text'

		for i in range(0, len(cipher_text), 2):
			c1 = int(cipher_text[i])
			c2 = int(cipher_text[i + 1])

			s = mod_exp(c1, x, p)
			decrypted = (c2 * mod_exp(s, p - 2, p)) % p

			decrypted_text.append(decrypted)


		decrypted_str = decode(decrypted_text, self.bits)
		decrypted_str = ''.join([ch for ch in decrypted_str if ch != '\x00'])

		return decrypted_str