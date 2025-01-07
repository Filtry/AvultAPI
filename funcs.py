import json


def downname(scene:str,q:str):
    #return f'&filename='+name.replace(':','').replace(' ','-').lower()++q+'.mp4'
    name=scene['title']
    meta=scene['brandMeta']['shortName']
    for i in ["'",':','(',')','"',',','.','#','-','&','@']:
        name=name.replace(i,'')
    return f"&filename={meta.lower()}-{name.replace(' ','-').lower()}-{q}.mp4"

def vidChk(v):
    for i in v['videos']['full']['files']:
        if i['format']=='320p' and i['multiCdnId']=="sceneAdaptiveCdn":
            return True
    return False

def err2k(v):
    if isinstance(v, list): return False
    return True

def retTrailer(scene):
    for ch in scene['children']:
        if ch['type']=='trailer' and ch['videos']!=[]:
            if ch['videos']['full']['files']!=[]:
                trailer=ch['videos']['full']['files']
            else:
                return (None,None)
            p=[int(i['format'].replace('p','')) for i in trailer]
            p.sort()
            maxRes=p[-1]
            return (maxRes,trailer)
    return (None,None)

def mergeParams(val):
    if val==None:
        return None
    elif len(val)==1:
        return val[0]
    else:
        return ';'.join((str(x) for x in val))

def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

def parentChk(data:dict):
    if 'parent' in data['result'].keys():
        return {'type':data['result']['parent']['type'],
                'title':data['result']['parent']['title'],
                'sceneIds':[i['id'] for i in data['result']['parent']['children'] if i['type']=='scene']}
    return None

def saveSettings(settings:dict):
    with open('settings.json','w') as sett:
        json.dump(settings,sett,indent=4)
    sett.close()

'''
def actorFilters(data:dict) -> dict:
    #data=api.getActorFilters()
    return {'tags':{i['id']:i['name'] for i in data['availableTags']},
           'channels':{i['id']:i['name'] for i in data['availableCollections']}}

def sceneFilters(data:dict) -> dict:
    #data=api.getSceneFilters()
    return {'tags':{i['id']:i['name'] for i in data['availableTags']},
           'channels':{i['id']:i['name'] for i in data['availableCollections']}}
'''
def procFilters(data:dict) -> dict:
    #data=api.getSceneFilters()
    return {'tags':{i['id']:i['name'] for i in data['availableTags']},
           'channels':{i['id']:i['name'] for i in data['availableCollections']}}
