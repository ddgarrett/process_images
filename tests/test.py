

data = {
    'root': {
        'child1': {
            '' : ['a','list']
        },
        'child2': {
            'child 2,1':{
                '':[1,2,3]
            },
            'child 2,2': {
                "":[4,5,6]
            },
            '':[7,8,9]
        }
     }
}

def traverse(key,value,indent):
    # print(type(key),type(value))
    indent += 4
    if key == '':
        for v in value:
            print(' '*indent,v)
    else:
        print(' '*indent,key)
        for k,v in value.items():
            traverse(k,v,indent)

for k,v in data.items():
    traverse(k,v,-4)

print(data)