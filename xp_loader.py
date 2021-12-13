from typing import Tuple
import numpy as np
import tcod

from tile_types import graphic_dt, tile_dt

##################################
# In-memory XP format is as follows:
# Returned structure is a dictionary with the keys version, layers, width, height, and layer_data
## Version is stored in case it's useful for someone, but as mentioned in the format description it probably won't be unless format changes happen
## Layers is a full 32 bit int, though right now REXPaint only exports or manages up to 4 layers
## Width and height are extracted from the layer with largest width and height - this value will hold true for all layers for now as per the format description
## layer_data is a list of individual layers, which are stored in the following format
### Each layer is a dictionary with keys width, height (see above), and cells. 
### Cells is a row major 2d array of, again, dictionaries with the values 'keycode' (ascii keycode), 'fore_r/g/b', and 'back_r/g/b' (technically ints but in value 0-255)
##################################

cp437 = np.array(
        [
            0x0000, 0x263A, 0x263B, 0x2665, 0x2666, 0x2663, 0x2660, 0x2022,
            0x25D8, 0x25CB, 0x25D9, 0x2642, 0x2640, 0x266A, 0x266B, 0x263C,
            0x25BA, 0x25C4, 0x2195, 0x203C, 0x00B6, 0x00A7, 0x25AC, 0x21A8,
            0x2191, 0x2193, 0x2192, 0x2190, 0x221F, 0x2194, 0x25B2, 0x25BC,
            0x0020, 0x0021, 0x0022, 0x0023, 0x0024, 0x0025, 0x0026, 0x0027,
            0x0028, 0x0029, 0x002A, 0x002B, 0x002C, 0x002D, 0x002E, 0x002F,
            0x0030, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036, 0x0037,
            0x0038, 0x0039, 0x003A, 0x003B, 0x003C, 0x003D, 0x003E, 0x003F,
            0x0040, 0x0041, 0x0042, 0x0043, 0x0044, 0x0045, 0x0046, 0x0047,
            0x0048, 0x0049, 0x004A, 0x004B, 0x004C, 0x004D, 0x004E, 0x004F,
            0x0050, 0x0051, 0x0052, 0x0053, 0x0054, 0x0055, 0x0056, 0x0057,
            0x0058, 0x0059, 0x005A, 0x005B, 0x005C, 0x005D, 0x005E, 0x005F,
            0x0060, 0x0061, 0x0062, 0x0063, 0x0064, 0x0065, 0x0066, 0x0067,
            0x0068, 0x0069, 0x006A, 0x006B, 0x006C, 0x006D, 0x006E, 0x006F,
            0x0070, 0x0071, 0x0072, 0x0073, 0x0074, 0x0075, 0x0076, 0x0077,
            0x0078, 0x0079, 0x007A, 0x007B, 0x007C, 0x007D, 0x007E, 0x007F,
            0x00C7, 0x00FC, 0x00E9, 0x00E2, 0x00E4, 0x00E0, 0x00E5, 0x00E7,
            0x00EA, 0x00EB, 0x00E8, 0x00EF, 0x00EE, 0x00EC, 0x00C4, 0x00C5,
            0x00C9, 0x00E6, 0x00C6, 0x00F4, 0x00F6, 0x00F2, 0x00FB, 0x00F9,
            0x00FF, 0x00D6, 0x00DC, 0x00A2, 0x00A3, 0x00A5, 0x20A7, 0x0192,
            0x00E1, 0x00ED, 0x00F3, 0x00FA, 0x00F1, 0x00D1, 0x00AA, 0x00BA,
            0x00BF, 0x2310, 0x00AC, 0x00BD, 0x00BC, 0x00A1, 0x00AB, 0x00BB,
            0x2591, 0x2592, 0x2593, 0x2502, 0x2524, 0x2561, 0x2562, 0x2556,
            0x2555, 0x2563, 0x2551, 0x2557, 0x255D, 0x255C, 0x255B, 0x2510,
            0x2514, 0x2534, 0x252C, 0x251C, 0x2500, 0x253C, 0x255E, 0x255F,
            0x255A, 0x2554, 0x2569, 0x2566, 0x2560, 0x2550, 0x256C, 0x2567,
            0x2568, 0x2564, 0x2565, 0x2559, 0x2558, 0x2552, 0x2553, 0x256B,
            0x256A, 0x2518, 0x250C, 0x2588, 0x2584, 0x258C, 0x2590, 0x2580,
            0x03B1, 0x00DF, 0x0393, 0x03C0, 0x03A3, 0x03C3, 0x00B5, 0x03C4,
            0x03A6, 0x0398, 0x03A9, 0x03B4, 0x221E, 0x03C6, 0x03B5, 0x2229,
            0x2261, 0x00B1, 0x2265, 0x2264, 0x2320, 0x2321, 0x00F7, 0x2248,
            0x00B0, 0x2219, 0x00B7, 0x221A, 0x207F, 0x00B2, 0x25A0, 0x00A0,
        ])

##################################
# Used primarily internally to parse the data, feel free to reference them externally if it's useful. 
# Changing these programattically will, of course, screw up the parsing (unless the format changes and you're using an old copy of this file)
##################################

version_bytes = 4
layer_count_bytes = 4

layer_width_bytes = 4
layer_height_bytes = 4
layer_keycode_bytes = 4
layer_fore_rgb_bytes = 3
layer_back_rgb_bytes = 3
layer_cell_bytes = layer_keycode_bytes + layer_fore_rgb_bytes + layer_back_rgb_bytes



##################################
# REXPaint color key for transparent background colors. Not directly used here, but you should reference this when calling libtcod's console_set_key_color on offscreen consoles.
##################################

transparent_cell_back_r = 255
transparent_cell_back_g = 0
transparent_cell_back_b = 255

####################################################################
# START LIBTCOD SPECIFIC CODE

##################################
# Used primarily internally to parse the data, feel free to reference them externally if it's useful. 
# Changing these programattically will, of course, screw up the parsing (unless the format changes and you're using an old copy of this file)
##################################

#the solid square character
poskey_tile_character = 219

#some or all of the below may appear in libtcod's color definitions; and in fact, you can use libtcod colors as you please for position keys. 
#These are merely the colors provided in the accompanying palette.

poskey_color_red = tcod.Color(255, 0, 0)
poskey_color_lightpurple = tcod.Color(254, 0, 255) # specifically 254 as 255, 0, 255 is considered a transparent key color in REXPaint
poskey_color_orange = tcod.Color(255, 128, 0)
poskey_color_pink = tcod.Color(255, 0, 128)
poskey_color_green = tcod.Color(0, 255, 0)
poskey_color_teal = tcod.Color(0, 255, 255)
poskey_color_yellow = tcod.Color(255, 255, 0)
poskey_color_blue = tcod.Color(0, 0, 255)
poskey_color_lightblue = tcod.Color(0, 128, 255)
poskey_color_purple = tcod.Color(128, 0, 255)
poskey_color_white = tcod.Color(255, 255, 255)

##################################
# please note - this function writes the contents of transparent cells to the provided console. 
# If you're building an offscreen console and want to use the default (or some other) color for transparency, please call libtcod's console.set_key_color(color)
##################################

def load_layer_to_console(console, xp_file_layer):
	if not xp_file_layer['width'] or not xp_file_layer['height']:
		raise AttributeError('Attempted to call load_layer_to_console on data that didn\'t have a width or height key, check your data')

	for x in range(xp_file_layer['width']):
		for y in range(xp_file_layer['height']):
			cell_data = xp_file_layer['cells'][x][y]
			fore_color = tcod.Color(cell_data['fore_r'], cell_data['fore_g'], cell_data['fore_b'])
			back_color = tcod.Color(cell_data['back_r'], cell_data['back_g'], cell_data['back_b'])
			tcod.console_put_char_ex(console, x, y, cell_data['keycode'], fore_color, back_color)

def get_position_key_xy(xp_file_layer, poskey_color):
	for x in range(xp_file_layer['width']):
		for y in range(xp_file_layer['height']):
			cell_data = xp_file_layer['cells'][x][y]
			if cell_data['keycode'] == poskey_tile_character:
				fore_color_matches = cell_data['fore_r'] == poskey_color.r and cell_data['fore_g'] == poskey_color.g and cell_data['fore_b'] == poskey_color.b
				back_color_matches = cell_data['back_r'] == poskey_color.r and cell_data['back_g'] == poskey_color.g and cell_data['back_b'] == poskey_color.b
				if fore_color_matches or back_color_matches:
					return (x, y)
	raise LookupError('No position key was specified for color ' + str(poskey_color) + ', check your .xp file and/or the input color')


# END LIBTCOD SPECIFIC CODE
####################################################################




##################################
# loads in an xp file from an unzipped string (gained from opening a .xp file with gzip and calling .read())
# reverse_endian controls whether the slices containing data for things like layer width, height, number of layers, etc. is reversed 
# so far as I can tell Python is doing int conversions in big-endian, while the .xp format stores them in little-endian
# I may just not be aware of it being unneeded, but have it there in case
##################################

def load_xp_string(file_string, reverse_endian=True):

	offset = 0

	version = file_string[offset : offset + version_bytes]
	offset += version_bytes
	layer_count = file_string[offset : offset + layer_count_bytes]
	offset += layer_count_bytes

	if reverse_endian:
		version = version[::-1]
		layer_count = layer_count[::-1]

	# hex-encodes the numbers then converts them to an int
	version = int(version.hex(), 16)
	layer_count = int(layer_count.hex(), 16)

	layers = []

	current_largest_width = 0
	current_largest_height = 0

	for layer in range(layer_count):
		#slight lookahead to figure out how much data to feed load_layer

		this_layer_width = file_string[offset:offset + layer_width_bytes]
		this_layer_height = file_string[offset + layer_width_bytes:offset + layer_width_bytes + layer_height_bytes]

		if reverse_endian:
			this_layer_width = this_layer_width[::-1]
			this_layer_height = this_layer_height[::-1]

		this_layer_width = int(this_layer_width.hex(), 16)
		this_layer_height = int(this_layer_height.hex(), 16)

		current_largest_width = max(current_largest_width, this_layer_width)
		current_largest_height = max(current_largest_height, this_layer_height)

		layer_data_size = layer_width_bytes + layer_height_bytes + (layer_cell_bytes *  this_layer_width * this_layer_height)

		layer_data_raw = file_string[offset:offset + layer_data_size]
		layer_data = parse_layer(file_string[offset:offset + layer_data_size], reverse_endian)
		layers.append(layer_data)

		offset += layer_data_size

	return {
		'version':version,
		'layer_count':layer_count,
		'width':current_largest_width,
		'height':current_largest_height,
		'layer_data':layers
	}

##################################
# Takes a single layer's data and returns the format listed at the top of the file for a single layer.
##################################

def parse_layer(layer_string, reverse_endian=True):
	offset = 0

	width = layer_string[offset:offset + layer_width_bytes]
	offset += layer_width_bytes
	height = layer_string[offset:offset + layer_height_bytes]
	offset += layer_height_bytes

	if reverse_endian:
		width = width[::-1]
		height = height[::-1]

	width = int(width.hex(), 16)
	height = int(height.hex(), 16)

	cells = []
	for x in range(width):
		row = []

		for y in range(height):
			cell_data_raw = layer_string[offset:offset + layer_cell_bytes]
			cell_data = parse_individual_cell(cell_data_raw, reverse_endian)
			row.append(cell_data)
			offset += layer_cell_bytes

		cells.append(row)

	return {
		'width':width,
		'height':height,
		'cells':cells
	}

##################################
# Pulls out the keycode and the foreground/background RGB values from a single cell's data, returning them in the format listed at the top of this file for a single cell.
##################################

def parse_individual_cell(cell_string, reverse_endian=True):
	offset = 0

	keycode = cell_string[offset:offset + layer_keycode_bytes]
	if reverse_endian:
		keycode = keycode[::-1]
	keycode = int(keycode.hex(), 16)
	offset += layer_keycode_bytes

	fore_r = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1
	fore_g = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1
	fore_b = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1

	back_r = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1
	back_g = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1
	back_b = int(cell_string[offset:offset+1].hex(), 16)
	offset += 1

	keycode = cp437[keycode]
	return (keycode, (fore_r, fore_g, fore_b), (back_r, back_g, back_b))
