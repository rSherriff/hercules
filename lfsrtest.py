from ctypes import c_uint32

count = 51*30
#count = 1
print("Map size: " + str(count) + " " + "{0:b}".format(count))

feedback = c_uint32(0x62B).value
print("Feedback: " + str(feedback) + " " + "{0:b}".format(feedback))

processed_tiles = []

tile = c_uint32(1).value
while(count >= 0):
    """
    #print("/////////////////////////////////////////////////")
    #print("Old tile: " + "{0:b}".format(tile))
    feedback_this_step = (-(tile & c_uint32(1).value) & feedback)
    #print("Feedback this step: " + "{0:b}".format(feedback_this_step))
    tile = (tile >> 1) ^ feedback_this_step
    #print("New tile: " + "{0:b}".format(tile))
    if tile not in processed_tiles:
        processed_tiles.append(tile)
    else:
        print("Adding a duplicate!")
        count = 0
    """
    if tile & 1:
        tile = (tile >> 1) ^ feedback
    else:
        tile = (tile >> 1)

    if tile not in processed_tiles:
        processed_tiles.append(tile)
    else:
        print("Adding a duplicate!")
        count = -1

    #count -= 1


processed_tiles.sort()
for x in processed_tiles:
    print(x)
    pass
    
print(len(processed_tiles))

