from functools import partial
import json
import os
from PIL import Image
import sys
import time
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import ttk
import tkinter.font as font

args = {
	'-r': "", # Reference PNG
	'-b': "", # Texture Dir
	'-o': "", # Output JSON
	'-l': "", # Limit Output
	'-w': "", # Whitelist
	'-k': "", # Blacklist
	'--config': False, # Use Config
	'--prompt': False, # Prompt User
}
root = tk.Tk()
frm = ttk.Frame(root, padding=10)

# Main function
def main():
	global args
	default_args = {
		'-r': "", # Reference PNG
		'-b': "", # Texture Dir
		'-o': "", # Output JSON
		'-l': "", # Limit Output
		'-w': "", # Whitelist
		'-k': "", # Blacklist
		'--config': False, # Use Config
		'--prompt': False, # Prompt User
	}
	
	read_config = "n"
	if (args == default_args):
		gui_main()
	elif (args["--config"] == True):
		read_config = "y"
	elif (args["--prompt"] == True):
		read_config = input("Would you like to read from the configuration file ([y]es*|[n]o)?")
	
	if (read_config in ["No", "NO", "no", "n", "N"]): # Go into prompting user for questions
		print("Using argument values over prompting.")
		if ((args == None) or (args["-r"] == "")): # If arg wasn't given
			reference_png_name = input("What is the image you want to copy (*'../Redstone Survivalist Skin.png')? ")
			reference_png_name = valid_ref_png(reference_png_name)
		else:
			reference_png_name = valid_ref_png(args["-r"])

		if ((args == None) or (args["-b"] == "")): # If arg wasn't given
			resource_pack_dir_path = input("What is the directory of block textures (*'../1-17-1_blocks/')? ")
			resource_pack_dir_path = valid_dir_name(resource_pack_dir_path)
		else:
			resource_pack_dir_path = valid_dir_name(args["-b"])

		if ((args == None) or (args["-o"] == "")): # If arg wasn't given
			results_filename = input("Where do you want to store the results (*'./results.json')? ")
			results_filename = valid_res_json(results_filename)
		else:
			results_filename = valid_res_json(args["-o"])

		if ((args == None) or (args["-l"] == "")): # If arg wasn't given
			top_n = input("How many of the top results do you want to store (*'10')? ")
			top_n = valid_top_n(top_n)
		else:
			top_n = valid_top_n(args["-l"])
		
		if ((args == None) or (args["-w"] == "")): # If arg wasn't given
			wl_name = input("What is the name of the whitelist file (*'whitelist.txt')? ")
			wl_name = valid_whitelist_name(wl_name)
		else:
			wl_name = valid_whitelist_name(args["-w"])

		if ((args == None) or (args["-k"] == "")): # If arg wasn't given
			bl_name = input("What is the name of the blacklist file (*'blacklist.txt')? ")
			bl_name = valid_blacklist_name(bl_name)
		else:
			bl_name = valid_blacklist_name(args["-k"])

	else:
		print("Reading configuration file. Using them over any arguments.")
		config = load_config()
		reference_png_name = config['ref_png_name']
		resource_pack_dir_path = config['pack_dir_path']
		results_filename = config['res_filename']
		top_n = config['top_n_results']
		bl_name = config['blacklist']
		wl_name = config['whitelist']

	run_program([reference_png_name, resource_pack_dir_path, results_filename, top_n, bl_name, wl_name])

# Function that saves the block colours to a dictionary
def find_block_colours(block_dir, list_blocks, whitelist, blacklist):
	block_cols = {}
	for block in list_blocks: # Go through all the blocks
		if ((whitelist != []) and (block not in whitelist)):
			continue
		if (block in blacklist):
			continue
		block_rgb, block_area = get_block_data(f"{block_dir}{block}.png")
		block_r, block_g, block_b, block_a = get_average_block_colour(block_rgb, block_area)
		block_cols[block] = {
			'r': block_r,
			'g': block_g,
			'b': block_b,
			'a': block_a
		}

	return block_cols


# Function that finds the error between the block and the pixel
def find_error(block_col, pixel_col):
	diff_r = abs(block_col[0] - pixel_col[0])/255 # red
	diff_g = abs(block_col[1] - pixel_col[1])/255 # green
	diff_b = abs(block_col[2] - pixel_col[2])/255 # blue
	diff_a = abs(block_col[3] - pixel_col[3])/255 # alpha

	diff_overall = 1 - (diff_r+diff_g+diff_b+diff_a) / 4

	return diff_overall

# Function to give a similarity score to all blocks (from 0 to 1)
def find_matches(block_rgba, pixel_col, x, y):
	matches = {}

	if (pixel_col[3] == 0): # If pixel is completely transparent
		return

	for block in block_rgba: # Go through all the blocks
		block_col = [block_rgba[block]['r'], block_rgba[block]['g'], block_rgba[block]['b'], block_rgba[block]['a']]
		error = find_error(block_col, pixel_col)
		matches[block] = error
	
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

# Function that loads the GUI
def gui_main():
	global frm, root
	root.title("PNG to MC Blocks Converter")
	frm.grid()

	# Header
	ttk.Label(frm, text="PNG to MC Blocks Converter", font=("Arial", 24)).grid(column=1, row=1, columnspan=5)

	# Left Labels
	left_labels = ["PNG File: ", "Block Dir: ", "Results File: ", "Limit: "]
	for idx, name in enumerate(left_labels):
		ttk.Label(frm, text=name, font=("Arial", 16)).grid(column=1, row=idx+2, sticky='w')
	
	# Right Labels
	right_labels = ["Whitelist: ", "Blacklist: "]
	for idx, name in enumerate(right_labels):
		ttk.Label(frm, text=name, font=("Arial", 16)).grid(column=4, row=idx+2, sticky='w')

	# Buttons
	search_button = tk.Button(frm, text="Search", font=("Arial", 16), command=run_program)
	search_button.grid(column=4, row=5)
	exit_button = tk.Button(frm, text="Exit", font=("Arial", 16), command=sys.exit)
	exit_button.grid(column=5, row=5)

	# Inputs
	png_button = tk.Button(frm, text="*.PNG", font=("Arial", 12))
	png_button.grid(column=2, row=2, sticky='w')
	png_button["command"] = partial(gui_select_update_text, png_button, "ref_png")

	block_dir_button = tk.Button(frm, text=".*/", font=("Arial", 12))
	block_dir_button.grid(column=2, row=3)
	block_dir_button["command"] = partial(gui_select_update_text, block_dir_button, "block_dir")

	results_file_button = tk.Button(frm, text="*.JSON", font=("Arial", 12))
	results_file_button.grid(column=2, row=4)
	results_file_button["command"] = partial(gui_select_update_text, results_file_button, "res_file")

	limit_button = tk.Button(frm, text="NUM", font=("Arial", 12))
	limit_button.grid(column=2, row=5)
	limit_button["command"] = partial(gui_select_update_text, limit_button, "limit")

	whitelist_button = tk.Button(frm, text="*.TXT", font=("Arial", 12))
	whitelist_button.grid(column=5, row=2)
	whitelist_button["command"] = partial(gui_select_update_text, whitelist_button, "wl")

	blacklist_button = tk.Button(frm, text="*.TXT", font=("Arial", 12))
	blacklist_button.grid(column=5, row=3)
	blacklist_button["command"] = partial(gui_select_update_text, blacklist_button, "bl")

	root.mainloop()
	sys.exit()

# Function that updates the GUI
def gui_select_update_text(button, input_name):
	global args

	try:
		if (input_name == "ref_png"):
			path = filedialog.askopenfilename()
			button["text"] = path.split("/")[-1]
			args["-r"] = path

		elif (input_name == "res_file"):
			path = filedialog.askopenfilename()
			button["text"] = path.split("/")[-1]
			args["-o"] = path

		elif (input_name == "wl"):
			path = filedialog.askopenfilename()
			button["text"] = path.split("/")[-1]
			args["-w"] = path

		elif (input_name == "bl"):
			path = filedialog.askopenfilename()
			button["text"] = path.split("/")[-1]
			args["-k"] = path

		elif (input_name == "block_dir"):
			path = filedialog.askdirectory()
			button["text"] = path.split("/")[-1]
			args["-b"] = f"{path}/"

		elif (input_name == "limit"):
			num = simpledialog.askinteger("Limit Results", "Limit the number of results: ")
			button["text"] = num
			args["-l"] = num
		
	except AttributeError:
		pass

	
# Function to load the configuration from the config file
def load_config(name="config.json"):
	try:
		with open(name, 'r') as config_file:
			config = json.load(config_file)
		
		return config
	except FileNotFoundError:
		print("Config file not found! Exiting...")
		sys.exit(1)

# Function that loads the blacklist of blocks
def load_blacklist(name):
	try:
		with open(name, 'r') as blacklist_file:
			blacklist = blacklist_file.read().splitlines()
			
		return blacklist
	except FileNotFoundError:
		print("Blacklist file not found! Exiting...")
		sys.exit(1)

# Function that loads the whitelist of blocks
def load_whitelist(name):
	try:
		with open(name, 'r') as whitelist_file:
			whitelist = whitelist_file.read().splitlines()
			
		return whitelist
	except FileNotFoundError:
		print("Whitelist file not found! Exiting...")
		sys.exit(1)

# Function responsible for reading args
def read_args():
	global args
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
		print("'-w <file>'	= Whitelist File")
		print("'-k <file>'	= Blacklist File")
		print("'--config'	= Use Configuration")
		print("'--prompt'	= Prompt User")

	else:
		for i in range(1, len(sys.argv)):
			if ((i+1 <= len(sys.argv)-1) and (sys.argv[i] in ['-r', '-b', '-o', '-l', '-w', '-k'])):
				args[sys.argv[i]] = sys.argv[i+1]
			elif (sys.argv[i] in ['--config', '--prompt']):
				args[sys.argv[i]] = True

	return args

# Function to run the program
def run_program(param=None):
	status_label = None
	if (param != None): # If passed from main function (rather than from gui)
		reference_png_name = param[0]
		resource_pack_dir_path = param[1]
		results_filename = param[2]
		top_n = param[3]
		bl_name = param[4]
		wl_name = param[5]
	else:
		status_label = tk.Label(frm, text="Completed!", font=("Arial", 16))
		status_label.grid(column=4, row=4, columnspan=2, sticky='w')

		global args
		reference_png_name = args['-r']
		resource_pack_dir_path = args['-b']
		results_filename = args['-o']
		top_n = args['-l']
		bl_name = args['-k']
		wl_name = args['-w']

	blacklist = load_blacklist(bl_name)
	whitelist = load_whitelist(wl_name)

	ref_rgb, ref_w, ref_h = get_ref_data(reference_png_name)
	blocks = get_block_list(resource_pack_dir_path)
	block_cols = find_block_colours(resource_pack_dir_path, blocks, whitelist, blacklist)

	ref_count = 0
	results = {}

	for ref_pix in ref_rgb: # For every pixel
		x = ref_count % ref_w # Get the X position
		y = ref_count // ref_w # Get the Y position

		list_matches = find_matches(block_cols, ref_pix, x, y)
		results[f"({x},{y})"] = list_matches

		ref_count += 1
	
	sort_res = sort_results(results, top_n)
	save_results(results_filename, sort_res)

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

# Function that checks if the blacklist file is valid
def valid_blacklist_name(name):
	if (not name.endswith(".txt")):
		print("Must end in '.txt'; Defaulting to './blacklist.txt'")
		return "./blacklist.txt"
	
	return name

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

# Function that checks if the whitelist file is valid
def valid_whitelist_name(name):
	if (not name.endswith(".txt")):
		print("Must end in '.txt'; Defaulting to './whitelist.txt'")
		return "./whitelist.txt"
	
	return name


if __name__ == "__main__":
	read_args()
	
	main()