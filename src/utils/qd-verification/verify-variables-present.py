# 0 ==========
# ifelse energy-ahead-close > 0
# [ fd 1 ]
# [
#   ifelse energy-left-close > 0
#   [ lt 90 fd 1 ]
#   [
#     ifelse energy-right-close > 0
#     [ rt 90 fd 1 ]
#     [
#       ifelse energy-ahead-medium > 0
#       [ fd 4 ]
#       [
#         ifelse energy-left-medium > 0
#         [ lt 90 fd 4 ]
#         [
#           ifelse energy-right-medium > 0
#           [ rt 90 fd 4 ]
#           [
#             ifelse energy-ahead-far > 0
#             [ fd 7 ]
#             [
#               ifelse energy-left-far > 0
#               [ lt 90 fd 7 ]
#               [
#                 ifelse energy-right-far > 0
#                 [ rt 90 fd 7 ]
#                 [
#                   rt random-float 45
#                   lt random-float 45
#                   fd 1
#                 ]
#               ]
#             ]
#           ]
#         ]
#       ]
#     ]
#   ]
# ]

# checks if all variables are present in the code

def verify_variables_present(code):
    return ("energy-ahead-close" in code and
            "energy-left-close" in code and
            "energy-right-close" in code and
            "energy-ahead-medium" in code and
            "energy-left-medium" in code and
            "energy-right-medium" in code and
            "energy-ahead-far" in code and
            "energy-left-far" in code and
            "energy-right-far" in code)