import os, re

def analyze_data(file_content):
    pos_tuples = []
    startpoint = None
    for i in range(0,len(file_content)):
        if "CREATE TABLE" in file_content[i] and startpoint == None:
            startpoint = i
        elif "ENGINE" in file_content[i] and startpoint != None:
            pos_tuples.append((startpoint, i))
            startpoint = None

    table_definitions = {}
    table_name_pattern = re.compile(r'`(.*)`')
    datatype_pattern = re.compile(r'` ([a-zA-Z0-9)(]+)')
    defaut_pattern = re.compile(r'DEFAULT (.*),?')
    foreign_pattern = re.compile(r'.*FOREIGN KEY \((.*)\) REFERENCES (.*)\((.*)\)')
    primary_key_pattern = re.compile(r'.*PRIMARY KEY \(`(.*)`\)')

    for position in pos_tuples:
        for i in range(position[0], position[1]+1):
            if i == position[0]:
                table_name = table_name_pattern.findall(file_content[i])[0]
                table_definitions.setdefault(table_name, {})
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


            elif "PRIMARY" in file_content[i].upper():
                primary_key = primary_key_pattern.findall(file_content[i].upper())[0]
                table_definitions[table_name][attr_name].setdefault("PRIMARY KEY", primary_key)
            elif "FOREIGN" in file_content[i].upper():
                foreign_key_values = foreign_pattern.findall(file_content[i].upper())
                keyname = foreign_key_values[0]
                target_table = foreign_key_values[1]
                target_attribute = foreign_key_values[2]
                table_definitions[table_name][attr_name].setdefault("FOREIGN KEY", {"KEYNAME" : keyname, "TARGET_TABLE" : target_table, "TARGET_ATTR" : target_attribute})

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


def output_data(dictionary):
    # print(type(dictionary))
    for key in dictionary.keys():
        if type(dictionary[key]) == dict:
            output_data(dictionary[key])
        else:
            print(dictionary[key])

path = choose_file()
content_list = get_file_content(path)
tables = analyze_data(content_list)
output_data(tables)

