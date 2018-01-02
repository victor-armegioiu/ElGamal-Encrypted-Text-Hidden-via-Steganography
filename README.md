# ElGamal-Encrypted-Text-Hidden-via-Steganography

The purpose of this project consists of two subgoals : implementing the ElGamal encryption without using any preexisting number theory modules or libraries and embedding the cipher text created by the aforementioned method within the pixels of an image. The plaintext is easily recovered by extracting the ciphertext from the pixel encoding and using the decryption method provided in the 'elgamal' module.

The 'ntheory_utilities' module covers the implementation of several functions: 
* logarithmic modular exponentiation
* the computation of the Jacobi symbol 
* finding the primitive root of a cyclic multiplicative group (modulo a prime of the form 2 * q + 1 where q is a prime as well)
* fast computation of U_{n + 1} and V_{n + 1} (coefficients of the Lucas sequence)
* encoding and decoding plaintext messages into bytes


TODO : other modules and steganography part
