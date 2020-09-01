import os, re

def analyze_data(file_content):
    pos_tuples = []
    startpoint = None
    # Find table definitions
    for i in range(0,len(file_content)):
        # Start of table
        if "CREATE TABLE" in file_content[i] and startpoint == None:
            startpoint = i
        # End of table
        elif "ENGINE" in file_content[i] and startpoint != None:
            pos_tuples.append((startpoint, i))
            startpoint = None

    table_definitions = {}
    # Regex patterns
    table_name_pattern = re.compile(r'`(.*)`')
    datatype_pattern = re.compile(r'` ([a-zA-Z0-9)(]+)')
    defaut_pattern = re.compile(r'DEFAULT (.*),?')
    foreign_pattern = re.compile(r'.*FOREIGN KEY \((.*)\) REFERENCES (.*)\((.*)\)')
    primary_key_pattern = re.compile(r'.*PRIMARY KEY \(`(.*)`\)')

    for position in pos_tuples:
        # Iterate trough table definition
        for i in range(position[0], position[1]+1):
            # Table name definition
            if i == position[0]:
                table_name = table_name_pattern.findall(file_content[i])[0]
                table_definitions.setdefault(table_name, {})
            # Read table attributes
            elif not "ENGINE" in file_content[i].upper() and not "PRIMARY" in file_content[i].upper() and not "FOREIGN" in file_content[i].upper(): 
                attr_name = table_name_pattern.findall(file_content[i])[0]
                table_definitions[table_name].setdefault(attr_name, {})

                datatype = datatype_pattern.findall(file_content[i])[0]
                table_definitions[table_name][attr_name].setdefault("DATATYPE", datatype)

                if "NOT NULL" in file_content[i].upper():
                    table_definitions[table_name][attr_name].setdefault("NULLABLE", False)
                else:
                    table_definitions[table_name][attr_name].setdefault("NULLABLE", True)

                if "AUTO_INCREMENT" in file_content[i].upper():
                    table_definitions[table_name][attr_name].setdefault("AUTO_INCREMENT", True)

                if "DEFAULT" in file_content[i].upper():
                    default_value = defaut_pattern.findall(file_content[i].upper())[0]
                    default_value = default_value.strip(" ")
                    default_value = default_value.strip(",")
                    default_value = default_value.strip("'")

                    if default_value == "":
                        default_value = "NULL"

                    table_definitions[table_name][attr_name].setdefault("DEFAULT VALUE", default_value)
                    # print('"' + default_value + '"')

            # Get primary key
            elif "PRIMARY" in file_content[i].upper():
                primary_key = primary_key_pattern.findall(file_content[i].upper())[0]
                table_definitions[table_name].setdefault("PRIMARY KEY", primary_key)
            # Get foreign key
            elif "FOREIGN" in file_content[i].upper():
                foreign_key_values = foreign_pattern.findall(file_content[i].upper())
                keyname = foreign_key_values[0]
                target_table = foreign_key_values[1]
                target_attribute = foreign_key_values[2]
                table_definitions[table_name].setdefault("FOREIGN KEY", {"KEYNAME" : keyname, "TARGET_TABLE" : target_table, "TARGET_ATTR" : target_attribute})

    return table_definitions

def choose_file():
    while True:
        path = input("Pfad zur SQL-Datei angeben: ")
        if path.startswith('"'):
            path = path.strip('"')
        if os.path.exists(path) and os.path.isfile(path):
            return path
        else:
            print("Datei {} konnte nicht gefunden werden".format(path))


def get_file_content(path):
    file_reader = open(path)
    file_content = file_reader.read()
    file_content = file_content.split("\n")
    return file_content


def output_data(dictionary, depth=0):
    for key in dictionary.keys():
        print("\t"*depth + key.upper())
        if type(dictionary[key]) == dict:
            depth += 1
            output_data(dictionary[key], depth)
            depth -= 1
        else:
            print("\t"*depth + str(dictionary[key]).lower())
    input()

path = choose_file()
content_list = get_file_content(path)
tables = analyze_data(content_list)
output_data(tables)

