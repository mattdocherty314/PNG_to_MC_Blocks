import json
import os
from PIL import Image
import sys

# Main function
def main():
	args = read_args()
	
	read_config = "n"
	if (args["--config"] == True):
		read_config = "y"
	elif (args["--prompt"] == True):
		read_config = input("Would you like to read from the configuration file ([y]es*|[n]o)?")
	
	if (read_config in ["No", "NO", "no", "n", "N"]): # Go into prompting user for questions
		print("Using argument values over prompting.")
		if (args["-r"] == False): # If arg wasn't given
			reference_png_name = input("What is the image you want to copy (*'../Redstone Survivalist Skin.png')? ")
			reference_png_name = valid_ref_png(reference_png_name)
		else:
			reference_png_name = valid_ref_png(args["-r"])

		if (args["-b"] == False): # If arg wasn't given
			resource_pack_dir_path = input("What is the directory of block textures (*'../1-17-1_blocks/')? ")
			resource_pack_dir_path = valid_dir_name(resource_pack_dir_path)
		else:
			resource_pack_dir_path = valid_dir_name(args["-b"])

		if (args["-o"] == False): # If arg wasn't given
			results_filename = input("Where do you want to store the results (*'./results.json')? ")
			results_filename = valid_res_json(results_filename)
		else:
			results_filename = valid_res_json(args["-o"])

		if (args["-l"] == False): # If arg wasn't given
			top_n = input("How many of the top results do you want to store (*'10')? ")
			top_n = valid_top_n(top_n)
		else:
			top_n = valid_top_n(args["-l"])

	else:
		print("Reading configuration file. Using them over any arguments.")
		config = load_config()
		reference_png_name = config['ref_png_name']
		resource_pack_dir_path = config['pack_dir_path']
		results_filename = config['res_filename']
		top_n = config['top_n_results']

	ref_rgb, ref_w, ref_h = get_ref_data(reference_png_name)
	blocks = get_block_list(resource_pack_dir_path)

	ref_count = 0
	results = {}

	for ref_pix in ref_rgb: # For every pixel
		x = ref_count % ref_w # Get the X position
		y = ref_count // ref_w # Get the Y position

		list_matches = find_matches(resource_pack_dir_path, blocks, ref_pix, x, y)
		results[f"({x},{y})"] = list_matches

		ref_count += 1
	
	sort_res = sort_results(results, top_n)
	save_results(results_filename, sort_res)

# Function that finds the error between the block and the pixel
def find_error(block_col, pixel_col):
	diff_r = abs(block_col[0] - pixel_col[0])/255 # red
	diff_g = abs(block_col[1] - pixel_col[1])/255 # green
	diff_b = abs(block_col[2] - pixel_col[2])/255 # blue
	diff_a = abs(block_col[3] - pixel_col[3])/255 # alpha

	diff_overall = 1 - (diff_r+diff_g+diff_b+diff_a) / 4

	return diff_overall

# Function to give a similarity score to all blocks (from 0 to 1)
def find_matches(block_dir, list_blocks, pixel, x, y):
	matches = {}

	if (pixel[3] == 0): # If pixel is completely transparent
		return

	for block in list_blocks: # Go through all the blocks
		block_rgb, block_area = get_block_data(f"{block_dir}{block}.png")
		block_r, block_g, block_b, block_a = get_average_block_colour(block_rgb, block_area)

		error = find_error([block_r, block_g, block_b, block_a], pixel)
		matches[block] = error
	
	print(f"Completed ({x}, {y})!")
	
	return matches

# Function to average the colour of the block
def get_average_block_colour(block_rgb, block_area):
	avg_r = 0
	avg_g = 0
	avg_b = 0
	avg_a = 0

	for block_pix in block_rgb:
		try:
			avg_r += block_pix[0] / block_area # red
			avg_g += block_pix[1] / block_area # green
			avg_b += block_pix[2] / block_area # blue
			avg_a += block_pix[3] / block_area # alpha
		except IndexError:
			avg_r += 0
			avg_g += 0
			avg_b += 0
			avg_a += 0
		except TypeError:
			avg_r += 0
			avg_g += 0
			avg_b += 0
			avg_a += 0

	
	return avg_r, avg_g, avg_b, avg_a

# Function to get a list of valid blocks
def get_block_list(blocks_path):
	try:
		blocks = []
		resource_pack_dir = os.fsencode(blocks_path)

		for res_file in os.listdir(blocks_path): #List the files in the directory
			res_name = os.fsdecode(res_file)
			if (res_name.endswith(".png")): # If it is a texture file
				blocks.append(res_name[:-4])
		
		return blocks
	except FileNotFoundError:
		print("No block texture directory found! Exiting...")
		sys.exit(1)

# Function to get all the block texture data
def get_block_data(block_file):
	block_png = Image.open(block_file, 'r')
	block_png_rgb = list(block_png.getdata())
	block_w, block_h = block_png.size
	block_area = block_w * block_h
	block_png.close()

	return block_png_rgb, block_area	

# Function to get the data associated with the reference image
def get_ref_data(ref_name):
	try:
		ref_png = Image.open(ref_name, 'r')
		ref_png_pix_rgb = list(ref_png.getdata())
		ref_png_w, ref_png_h = ref_png.size
		ref_png.close()

		return ref_png_pix_rgb, ref_png_w, ref_png_h
	except FileNotFoundError:
		print("No reference PNG found! Exiting...")
		sys.exit(1)

# Function to load the configuration from the config file
def load_config(name="config.json"):
	with open(name, 'r') as config_file:
		config = json.load(config_file)
	
	return config

# Function responsible for reading args
def read_args():
	args = {
		'-r': False, # Reference PNG
		'-b': False, # Texture Dir
		'-o': False, # Output JSON
		'-l': False, # Limit Output
		'--config': False, # Use Config
		'--prompt': False, # Prompt User
	}
	if (len(sys.argv) == 1):
		return None

	elif ((len(sys.argv) == 2) and (sys.argv[1] in ["-h", "-?", "--help"])):
		print("Usage:")
		print("''		= Manual Input")
		print("'-h'		= Help")
		print("'-r <file>'	= Reference PNG")
		print("'-b <dir>'	= Texture Directory")
		print("'-o <file>'	= Output JSON")
		print("'-l <num>'	= Limit Output")
		print("'--config'	= Use Configuration")
		print("'--prompt'	= Prompt User")

	else:
		for i in range(1, len(sys.argv)):
			if ((i+1 <= len(sys.argv)-1) and (sys.argv[i] in ['-r', '-b', '-o', '-l'])):
				args[sys.argv[i]] = sys.argv[i+1]
			elif (sys.argv[i] in ['--config', '--prompt']):
				args[sys.argv[i]] = True

	return args

# Function to save the results to a JSON file
def save_results(name, results):
	with open(f"{name}", 'w') as results_file:
		json.dump(results, results_file, indent=2)

# Function to sort the results and limit them
def sort_results(results, limit_count):
	save_results = {}
	new_results = {}
	for idx, res in enumerate(results):
		if (results[res] == None):
			continue
		new_results[res] = dict((sorted(results[res].items(), key=lambda x: x[1], reverse=True))) # sort the results
		save_results[res] = {}
		for idx2, res2 in enumerate(new_results[res]):
			if (idx2 >= limit_count):
				break
			save_results[res][res2] = new_results[res][res2] # limit the results

	return save_results

# Function that checks if the directory name is valid
def valid_dir_name(name):
	if (not name.endswith("/")):
		print("Must end in '/'; Defaulting to '../1-17-1_blocks/'")
		return "../1-17-1_blocks/"
	
	return name

# Function that checks if the reference PNG name is valid
def valid_ref_png(name):
	if (not name.endswith(".png")):
		print("Must end in '.png'; Defaulting to '../Redstone Survivalist Skin.png'")
		return "../Redstone Survivalist Skin.png"
	
	return name

# Function that checks if the results filename is valid
def valid_res_json(name):
	if (not name.endswith(".json")):
		print("Must end in '.json'; Defaulting to './results.json'")
		return "./results.json"
	
	return name

# Function that checks if the top N is valid
def valid_top_n(name):
	if (not name.isnumeric()):
		print("Not a number; Defaulting to '10'")
		return 10
	
	return int(name)



if __name__ == "__main__":
	main()