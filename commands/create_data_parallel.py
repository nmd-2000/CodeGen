import json
import tree_sitter
from tree_sitter import Language, Parser
import os

from tqdm import tqdm

def get_function_list(node):
    def traverse_type(node, results, kind) -> None:
        if node.type in kind:
            results.append(node)
        if not node.children:
            return
        for n in node.children:
            traverse_type(n, results, kind)
    res = []
    traverse_type(node, res, ['function_item', 'expression_statement', 'ERROR'])
    return res

def get_function_name(function_node):
    assert type(function_node) == tree_sitter.Node
    # assert function_node.type == 'function_item'
    
    for child in function_node.children:
        if child.type == 'identifier':
            return child.text.decode()
    return None


if __name__ == '__main__':
    src_path = '/media/Z/dungnm31/unsafe_safe_rust/raw/unsafe.all.jsonl'
    tgt_path = '/media/Z/dungnm31/unsafe_safe_rust/raw/safe.all.jsonl'
    
    parser = Parser()
    parser.set_language(Language('/home/dungnm31/CodeGen/tree-sitter/rust.so', 'rust'))
    
    list_function_names = {}
    new_data_list = []
    
    with open(src_path, 'r') as file:
        src_data = list(file)
        
    with open(tgt_path, 'r') as file:
        tgt_data = list(file)
    
    for data in tqdm(src_data):
        data = json.loads(data)
        
        code = data['content']
        root = parser.parse(bytes(code, 'utf8')).root_node
        try:
            res = get_function_list(root)
            if not res:
                print(code)
            name = get_function_name(res[0])
            
        except RecursionError:
            continue
        
        if name == None:
            continue
        elif len(name) >= 8:
            list_function_names[name] = data
        
    print('================= Unsafe set', len(list_function_names))
    
    for data in tqdm(tgt_data):
        data = json.loads(data)
        
        code = data['content']
        
        root = parser.parse(bytes(code, 'utf8')).root_node
        try:
            res = get_function_list(root)
            safe_name = get_function_name(res[0])
            
        except RecursionError:
            continue
        
        if safe_name == None:
            continue
        elif safe_name in list_function_names.keys():
            new_data_list.append({'unsafe': list_function_names[safe_name], 'safe': data})
            list_function_names.pop(safe_name, None)
        
    print('parallel data:', len(new_data_list))
    
    with open('/media/Z/dungnm31/unsafe_safe_rust/raw/parallel.data.jsonl', 'a') as save_file:
        for data in tqdm(new_data_list):
            json.dump(data, save_file)
            save_file.write('\n')
