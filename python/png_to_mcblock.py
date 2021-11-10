import json
import os
from PIL import Image

# Main function
def main():
	reference_png_name = "../Redstone Survivalist Skin.png"
	resource_pack_dir_path = "../1-14-4_block/"
	results_filename = "results.json"

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
	
	sort_res = sort_results(results, 10)
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
	blocks = []
	resource_pack_dir = os.fsencode(blocks_path)

	for res_file in os.listdir(blocks_path): #List the files in the directory
		res_name = os.fsdecode(res_file)
		if (res_name.endswith(".png")): # If it is a texture file
			blocks.append(res_name[:-4])
	
	return blocks

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
	ref_png = Image.open(ref_name, 'r')
	ref_png_pix_rgb = list(ref_png.getdata())
	ref_png_w, ref_png_h = ref_png.size
	ref_png.close()

	return ref_png_pix_rgb, ref_png_w, ref_png_h

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



if __name__ == "__main__":
	main()