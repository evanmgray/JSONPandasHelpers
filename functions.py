
# Recursively converts JSON into list of key values
#  - Every nested key gets appended and separated by a period
#  - e.g. page,pageSize,count,list,list.id,list.type,etc. . .
def get_keys(d, parent_key=[], keys=None, excl_schema = False):
    if keys is None:
        keys = []
    
    #Iterate through dictionary items
    for k, v in d.items():
        #Guard clause to exclude schema
        if k == 'schema' and excl_schema: continue
        
        #Append the current key, or start with the current key if no parent
        if parent_key:
            new_key = f"{parent_key},\'{k}\'"
        else:
            new_key = f"\'{k}\'"
        
        #If the current key (with appended start) doesn't exist, append to list
        if new_key not in keys:
            keys.append(new_key)
        
        #If the current value is a dict, recursively call this function
        if isinstance(v, dict):
            get_keys(v, new_key, keys, excl_schema)
            
        #If the current value is a list, then we need to iterate though the values first to find other lists
        #(This only works because we don't have lists of lists in this output!)
        elif isinstance(v, type([])):
            for item in v:
                if isinstance(item, dict):
                    get_keys(item, new_key, keys, excl_schema)
                if isinstance(item, type([])):
                    print('WARNING: List of Lists Encountered')
                    
    return keys

#Recursive dictionary pull function
def get_nested_value(dictionary, keys, warn = True):
    for key in keys:
        try:
            dictionary = dictionary[key]
        except Exception as e:
            if warn == True: print(f"WARNING: Cannot find dictionary key for given record")
            dictionary = {}
            return dictionary
    return dictionary

# Pulls all the values in keys for all records
def get_record_values(dictionary, keys, warn = True, record_type = 'record'):
    #INPUT: dictionary is output from the API call
    #INPUT: keys is a list of keys within the list entry, e.g. ['properties','clause_fees','type']
    #INPUT: warn enables a message if a record does not have a value in keys
    #INPUT: record_type changes between 'record' and 'workflow'

    # Initialize
    dict_list = dictionary['list']
    output_df = pd.DataFrame()
    
    # Iterate through all records in the JSON and create the name andi d column
    name_list = []
    id_list = []
    for record in dict_list:
        if record_type == 'record': name = get_nested_value(record,['name'],warn)
        if record_type == 'workflow': name = get_nested_value(record,['title'],warn)
        id_val = get_nested_value(record,['id'],warn)
        name_list.append(name)
        id_list.append(id_val)
    
    if record_type == 'record': output_df['Name'] = name_list
    if record_type == 'workflow': output_df['Title'] = name_list
        
    output_df['Id'] = id_list
    
    # For each key, get value from each record
    for key in keys:
        value_list = []
        for record in dict_list:
            value = get_nested_value(record,key,warn) ###
            value_list.append(value)
        output_df['.'.join(key)] = value_list
        output_df['.'.join(key)] = output_df['.'.join(key)].astype(str)
    return output_df


def get_all_values_with_string(json_dict,contains_string,record_type = 'record'):
    # 1: Get list of lists with all fields
    keys = get_keys(json_dict)
    search_keys = []
    # 2: Scan JSON for each one, and check if value has a "$", returning new list
    for key in keys:
        if ('list' in key[:7]) & (',' in key[:7]):
            key = key[7:]
            key = key.replace("'", "").split(',')
            key = [key]
            values_df = get_record_values(json_dict,key,False)
            check_contains_string = values_df.iloc[:, 2].str.contains(contains_string).any()
            check_any_dict = values_df.iloc[:, 2].str.contains(r'\{.+\}', na=False).any()
            if (check_contains_string) & (not check_any_dict): search_keys.append(key[0])
    # 3: Get all values from that list
    output_df = get_record_values(json_dict,search_keys,False,record_type)
    return output_df