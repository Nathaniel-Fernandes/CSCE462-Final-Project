# # 7-segment display GPIO Pin Numbers
# # Data Sheet: https://cdn-shop.adafruit.com/datasheets/2155datasheet.pdf

# A_SEG = 29
# B_SEG = 31
# C_SEG = 33
# D_SEG = 35
# E_SEG = 37
# F_SEG = 32
# G_SEG = 36

# seven_segment = {
#     0: (A_SEG,B_SEG,C_SEG,D_SEG,E_SEG,F_SEG),
#     1: (B_SEG, C_SEG),
#     2: (A_SEG, B_SEG, D_SEG, E_SEG, G_SEG),
#     3: (A_SEG, B_SEG, C_SEG, D_SEG, G_SEG),
#     4: (B_SEG, C_SEG, F_SEG, G_SEG),
#     5: (A_SEG, C_SEG, D_SEG, F_SEG, G_SEG),
#     6: (A_SEG, C_SEG, D_SEG, E_SEG, F_SEG, G_SEG),
#     7: (A_SEG, B_SEG, C_SEG),
#     8: (A_SEG, B_SEG, C_SEG, D_SEG, E_SEG, F_SEG, G_SEG),
#     9: (A_SEG, B_SEG, C_SEG, F_SEG, G_SEG),
#     "all": (A_SEG, B_SEG, C_SEG, D_SEG, E_SEG, F_SEG, G_SEG)
# }

# # Traffic Light GPIO Pin Numbers (Pedestrian & Car)
# BUTTON = 40

# PED_RED = 12
# PED_GREEN = 18
# PED_BLUE = 16

# CAR_RED = 7
# CAR_GREEN = 11
# CAR_BLUE = 13

# # Intersection State
# COUNTDOWN_START_TIME = 0 # seconds
# COOLDOWN = 0 # seconds

# CABINET_STATE = {
#     # reset: turn all off
#     "reset": {
#         "instructions": [
#             ["off", (A_SEG, B_SEG, C_SEG, D_SEG, E_SEG, F_SEG, G_SEG, PED_RED, PED_GREEN, PED_BLUE, CAR_RED, CAR_GREEN, CAR_BLUE)],
#         ],
#         "next_state": "state1",
#         "condition": "immediate",
#         "condition_params": None 
#     },

#     # drawer is closed - waiting for open
#     "state1": {
#         "instructions": [["on", (CAR_GREEN, PED_RED)]],
#         "next_state": "state2",
#         "condition": "button_press", # will either use polling or interrupt to detect button press
#         "condition_params": None
#     },

#     # drawer is opened - waiting for close
#     "state2": {
#         "instructions": [["off", CAR_GREEN], ["blink", CAR_BLUE, 3], ["on", CAR_RED]],
#         "next_state": "state3",
#         "condition": "immediate",
#         "condition_params": None
#     },

#     # ped turns green, start counter from 9 to 0. transition when countdown <= 4
#     "state3": {
#         "instructions": [["off", PED_RED], ["on", PED_GREEN], ["startcoundown"]],
#         "next_state": "state4",
#         "condition": "countdown",
#         "condition_params": 4
#     },

#     # counter reaches 4, ped turns blue. When counter reaches 0, ped turns red + car green
#     "state4": {
#         "instructions": [["off", PED_GREEN], ["on", PED_BLUE]],
#         "next_state": "reset",
#         "condition": "countdown",
#         "condition_params": 0
#     }
# }