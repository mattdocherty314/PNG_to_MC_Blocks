import os
from PIL import Image

reference_png_name = "./Redstone Survivalist Skin.png"
resource_pack_dir_path = "../1-14-4_block/"

blocks = []
resource_pack_dir = os.fsencode(resource_pack_dir_path)
for res_file in os.listdir(resource_pack_dir):
    res_name = os.fsdecode(res_file)
    if (res_name.endswith(".png")):
        blocks.append(res_name[:-4])

ref_png = Image.open(reference_png_name, 'r')
ref_png_pix_rgb = list(ref_png.getdata())
ref_png_w, ref_png_h = ref_png.size
ref_png.close()

coordinates = []
ref_png_res_match = {}
ref_pix_count = 0
for ref_pix in ref_png_pix_rgb:
    x = ref_pix_count % ref_png_w
    y = ref_pix_count // ref_png_w
    
    if (ref_pix[3] != 0):
        ref_png_res_match[ref_pix_count] = {}
        for block in blocks:
            block_png = Image.open(resource_pack_dir_path+block+".png", 'r')
            block_png_pix_rgb = list(block_png.getdata())
            block_png_w, block_png_h = block_png.size
            block_png_area = block_png_w * block_png_h
            block_png.close()
            
            avg_block_r = 0
            avg_block_g = 0
            avg_block_b = 0
            avg_block_a = 0
            for block_pix in block_png_pix_rgb:
                try:
                    avg_block_r += block_pix[0] / block_png_area
                    avg_block_g += block_pix[1] / block_png_area
                    avg_block_b += block_pix[2] / block_png_area
                    avg_block_a += block_pix[3] / block_png_area
                except TypeError:
                    avg_block_r = 0
                    avg_block_g = 0
                    avg_block_b = 0
                    avg_block_a = 0
                except IndexError:
                    avg_block_r = 0
                    avg_block_g = 0
                    avg_block_b = 0
                    avg_block_a = 0

            pix_diff_r = abs(avg_block_r - ref_pix[0])/255
            pix_diff_g = abs(avg_block_g - ref_pix[1])/255
            pix_diff_b = abs(avg_block_b - ref_pix[2])/255
            pix_diff_a = abs(avg_block_a - ref_pix[3])/255

            pix_diff_overall = 1 - (pix_diff_r+pix_diff_g+pix_diff_b+pix_diff_a) / 4
            ref_png_res_match[ref_pix_count][block] = pix_diff_overall

        coordinates.append("("+str(x)+", "+str(y)+")")
    print("Completed ("+str(x)+", "+str(y)+")!")
    
    ref_pix_count += 1


results_filename = "./top20_results.txt"
results_file = open(results_filename, 'w')
ref_pix_count = 0

for ref_pix in ref_png_res_match:
    results_file.write(str(coordinates[ref_pix_count])+"\n")
    ref_png_res_chance_sort = sorted(ref_png_res_match[ref_pix].values(), reverse=True)[:20]
    for chance in ref_png_res_chance_sort:
        for match in ref_png_res_match[ref_pix]:
            if (ref_png_res_match[ref_pix][match] == chance):
                results_file.write(str(match) + ": "+ str(chance)+"\n")
                break

    results_file.write("\n")
    ref_pix_count += 1
results_file.close()