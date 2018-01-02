__author__ = "Andreea Musat"

import sys
import random
import pickle
from scipy import misc
from elgamal import *

MAX_LEN, CHANNEL = 100000, 2

"""
Display error message and exit
"""
def error(msg):
	print(msg)
	sys.exit(-1)

""" 
Transform a char string into a binary string, where each group of 
8 bits represents the ascii code of the corresponding symbol in the 
message.
"""
def str2binstr(message):
	result = ""
	for symbol in message:
		result += str(format(ord(symbol), 'b').zfill(8))
	return result

"""
Return a list of MAX_LEN pixel coordinates that will be used to
hide the message. If the method is 'range', the pixels are chosen
sequentially, starting with a point given by the key. Otherwise, 
they are chosen using a pseudorandom generator having the seed
given as a parameter.
"""
def get_pixel_indices(img, key, method):
	global MAX_LEN

	# make sure not to use more than half of the pixels in the channel
	MAX_LEN = int(min(0.5 * img.shape[0] * img.shape[1], MAX_LEN))

	if method == 'range':
		indices = [(i, j) for i in range(img.shape[0])\
						  for j in range(img.shape[1])]

		split_point = key % (img.shape[0] * img.shape[1])
		return indices[split_point:] + indices[:split_point]

	if method == 'rand':
		random.seed(hash(key))
		indices = set()

		while len(indices) < MAX_LEN:
			x = random.randint(0, img.shape[0] - 1)
			y = random.randint(0, img.shape[1] - 1)
			indices.add((x, y))
		
		return list(indices)
	
"""
ElGamal encryption. See elgamal.py for more details
"""
def encrypt(message):
	bits = 256
	key_gen = KeyGenerator(bits)
	
	elgam = ElGamal(key_gen, message, 'encrypt')
	cipher_text = elgam.encrypt()	

	cipher_text_len = len(cipher_text)
	info = (cipher_text_len, key_gen)

	pickle.dump(info, open('config.p', 'wb'))

	return cipher_text

"""
ElGamal decryption. See elgamal.py for more details
"""
def decrypt(message):
	cipher_text_len, key_gen = pickle.load(open("config.p", "rb"))

	elgam = ElGamal(key_gen, message[:cipher_text_len], 'decrypt')
	plain_text = elgam.decrypt()

	return plain_text

"""
Hide a secret message in the blue pixels of an input image. The output image
is 'stegano.png'. PNG format is chosen for the stegano image as it is lossless.
"""
def hide_message(message_file_name, image_file_name, key, method, lsb):
	# read image from input file
	try:
		img = misc.imread(image_file_name)
		misc.imsave('junk.png', img)
	except Exception:
		error("[ERROR] Image " + image_file_name + "not found")

	# read message from input file
	try:
		file = open(message_file_name, 'r')
		message = file.read()
	except Exception:
		error("[ERROR] Could not read message file " + message_file_name)
	
	# add the message length at the beginning of the actual message
	message = str(len(message)) + " " + message + " "

	# get the corresponding binary string
	binary_str_msg = str2binstr(encrypt(message))
	
	# pad the binary string with zeros to make sure the length of the message
	# is divisible by lsb
	binary_str_msg += '0' * (lsb - len(binary_str_msg) % lsb)
	
	# compute the number of pixels necessary to hide the data
	num_pixels = len(binary_str_msg) // lsb

	# get the coordinates of the pixels used for hiding the message
	indices = get_pixel_indices(img, key, method)
	
	# check the length of the message
	if len(indices) < num_pixels:
		error("[ERROR] Message too long")
	
	# only keed the needed pixels
	indices = indices[0:num_pixels]

	for cnt in range(num_pixels):
		# set last lsb bits of current blue pixel to zero
		img[indices[cnt][0], indices[cnt][1], CHANNEL] &= (255 - ((1 << lsb) - 1))

		# get new value of last lsb bits from the bit string
		img[indices[cnt][0], indices[cnt][1], CHANNEL] |= int(binary_str_msg[cnt * lsb : (cnt + 1) * lsb], 2)

	print("Your message has been successfully hidden in stegano.png")
	misc.imsave("stegano.png", img)

"""
Get the hidden message from a stegano input image. The message can be retrieved
only if the correct method and key are used.
"""
def reveal_message(image_file_name, message_file_name, key, method, lsb):
	# read stegano image
	try:
		img = misc.imread(image_file_name)
	except Exception:
		error("[ERROR] Image " + image_file_name + " not found")

	# get coordinates of pixels used for hiding the message
	indices = get_pixel_indices(img, key, method)
	
	# for each of those pixels, add the last lsb bits to bin_msg
	bin_msg = ""
	for cnt in range(len(indices)):
		bin_msg += bin(img[indices[cnt][0], indices[cnt][1], CHANNEL] & ((1 << lsb) - 1))[2:].zfill(lsb)

	# get the corresponding ascii message
	msg = ""
	for i in range(len(bin_msg) // 8):
		msg += chr(int(bin_msg[i * 8 : (i + 1) * 8], 2))

	# decrypt the message
	decrypted_msg = decrypt(msg)

	# the length of the message should be the first word of the text
	message_len_str = decrypted_msg.split(' ')[0]

	# the actual message begins after the first word
	start_index = len(message_len_str) + 1

	# try to get the integer message length (error if encoding was not made
	# using the same parameters)
	try:
		message_len = int(message_len_str)
	except Exception:
		print("[ERROR] Could not read message length.")
		sys.exit(-1)

	# write the decrypted message to the output file
	decrypted_msg = decrypted_msg[start_index:start_index + message_len]
	file = open(message_file_name, 'w')
	file.write(decrypted_msg)
	
	print("Your secret message can be found in " + message_file_name)

def main(args):
	if len(args) != 5:
		error("Usage: \npython stegano.py hide message_file_name image_file_name key OR\n"\
			           "python stegano.py reveal image_file_name decrypted_msg_file_name key")

	try:
		key = int(args[4])
	except Exception:
		error("[ERROR] Key should be an integer.")

	# choose embedding pixels randomly and use last 2 bits from the pixel
	method, lsb = 'rand', 2

	if args[1] == "hide":
		hide_message(args[2], args[3], key, method, lsb)
	elif args[1] == "reveal":
		reveal_message(args[2], args[3], key, method, lsb)
	else:
		print("Unknown action %s. Exiting...\n", args[1])

if __name__ == "__main__":
	main(sys.argv)