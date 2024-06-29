def display(response):
    print(response)
    lists = response.split('\n')
    if 'Raw Material:' not in response: raise AttributeError
    biggest = 0
    for i, list in enumerate(lists):
        st = list.find(':')
        lists[i] = [list[0:st], list[st+1:]]
        if lists[i][0] == '':
            lists.pop(i)
            continue
        li = lists[i][1]
        split = True
        pos = 0
        temp = []
        for j, let in enumerate(li):
            if let == '(': split = False
            elif let == ')': split = True
            if split and let == ',' or j == len(li)-1:
                t = li[pos:j+1]
                if t[-1] == ',': temp.append(t[0:-1].strip())
                else: temp.append(t.strip())
                pos = j+1
        if len(temp) > biggest: biggest = len(temp)
        lists[i][1] = temp

    print("INITIATING RESULT SEPERATION")
    dic = dict(lists)
    dic['ingredients'] = []
    if len(dic["Raw Material"]) <= 3: raise(AttributeError)
    for i, raw in enumerate(dic["Raw Material"]):
        if raw.find('(') != -1:
            st = raw.find('(')
            dic['ingredients'].append(raw[0:st])
            dic['Raw Material'][i] = raw[st+1:-1].split(',')
        else:
            dic['ingredients'].append(raw)
            dic['Raw Material'][i] = ['None']
            
    for i, al in enumerate(dic["allergies"]):
        if al.find('(') != -1:
            st = al.find('(')
            dic['allergies'][i] = al[st+1:-1].split(',')
        else:
            dic['allergies'][i] = ['None']
            
    for i, haz in enumerate(dic["hazards"]):
        if haz.find('(') != -1:
            st = haz.find('(')
            dic['hazards'][i] = haz[st+1:-1].split(',')
        else:
            dic['hazards'][i] = ['None']

    dic['components'] = dic['Raw Material']
    del dic['Raw Material']

    print(len(dic['allergies']),len(dic['hazards']), len(dic['ingredients']))
    
    if len(dic['allergies']) == len(dic['hazards']) == len(dic['ingredients']):print('positive response')
    else: raise AttributeError
        
    return dic