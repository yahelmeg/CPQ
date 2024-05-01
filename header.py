symbol_table = {}

temp_counter = 0  # Initialize temp_counter globally
label_counter = 0  # Initialize label_counter globally


def gen_temp():
    global temp_counter  # Declare temp_counter as global
    temp_counter += 1
    return f"t{temp_counter}"


def gen_label():
    global label_counter  # Declare temp_counter as global
    label_counter += 1
    return f"L{label_counter}"


def get_expression_type(type1,type2):
    if type1 == "float" or type2 == "float":
        return "float"
    else:
        return "int"
