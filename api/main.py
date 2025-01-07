from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.api import AiloLite
from typing import Union, Annotated, List
from filters import format_date, lowerName, blanks, chkType
from enums import ScenesSort, ActorsSort, GenderSort
from schema import SortSettings, SettingsModel
from fastapi_utils.tasks import repeat_every
from pagination import *
from funcs import *
import json
import re

app = FastAPI(title="AvultAPI Lite")
api = AiloLite()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.filters['format_date'] = format_date
templates.env.filters['lowerName'] = lowerName
templates.env.filters['type'] = chkType
settings=json.load(open('settings.json','r'))
api.resultLimit=settings['limit']
ScenesSortList=[i.value for i in ScenesSort]
ActorsSortList=[i.value for i in ActorsSort]
GendersSortList=[i.value for i in GenderSort]
siteIds=json.load(open('sites.json','r'))
sites={i:siteIds[i]['name'] for i in siteIds if siteIds[i]['show']==True}
actFilters=procFilters(api.getActorFilters())
scnFilters=procFilters(api.getSceneFilters())
#print(groupIds)
#refreshFilters()


#@repeat_every(seconds=30)
def CheckExpireAuth():
    print('30 seconds')
    if api.isExpired==True:
        print(api.expMsg)

@repeat_every(seconds=86400)
def refreshFilters():
    actFilters=procFilters(api.getActorFilters())
    scnFilters=procFilters(api.getSceneFilters())


@app.on_event('startup')
@repeat_every(seconds=30)
async def startup_event():
    t=api.loadFromFile()
    #await CheckExpireAuth()
    if t==False:
        print(api.expMsg)
    else:
        #print('Auth has been Set...')
        print('Expiry On:',api.getExpiryTime.isoformat())
    
def intValid(arg=None):
    if isinstance(arg,int): 
        return arg
    elif isinstance(arg,str): 
        #if re.match(r'^(\d+;)*\d+$', arg):
        if re.match(r'^(\d+;)*\d+$', arg):
            return arg
        else:
            raise HTTPException(status_code=404,detail="String must contain only numbers separated by ';'")
    elif type(arg)==None:
        return arg
    else: 
        ValueError('None Match')

def strValid(value: str) -> str:
    if value==None:
        return value
    if not re.match(r'^[a-zA-Z]+(;[a-zA-Z]+)*$', value):
        raise HTTPException(status_code=400,detail="Invalid format. Must be words separated by ';'.")
    return value

@app.get("/")
async def root():
    return RedirectResponse('/web/index')

@app.get('/api/scenes',tags=['Scenes'])
async def scenes(sort: ScenesSort = Query(settings['sort']['scenes']),search:str=None,tagId:Union[int, str]=None,sceneId:Union[int,str]=None,collectionId:Union[int, str]=None,actorId:Union[int, str]=None,brand:str=None,offset:int=0):
    #strValid(brand)
    intValid(actorId)
    intValid(tagId)
    intValid(collectionId)
    intValid(sceneId)
    return api.getScenes(sort,search,tagId,sceneId,collectionId,actorId,brand,offset)

@app.get('/api/scene/{sceneId}',tags=['Scenes'])
async def scene(sceneId:int):
    return api.getScene(sceneId)

@app.get('/api/actors',tags=['Actors'])
async def actors(sort:ActorsSort = Query(...),search:str=None,gender:GenderSort = Query(...),letter:str=None,tagId:Union[int, str]=None,collectionId:Union[int, str]=None,actorId:Union[int, str]=None,groupId:Union[int, str]=None,offset:int=0):
    intValid(groupId)
    intValid(actorId)
    intValid(tagId)
    intValid(collectionId)
    if gender=='all': gender=None
    return api.getActors(sort,search,gender,letter,tagId,collectionId,actorId,groupId,offset)

@app.get('/api/actor/{actorId}',tags=['Actors'])
async def actor(actorId:int):
    return api.getActor(actorId)

@app.get('/api/channels',tags=['Channels'])
async def channels(sort: ActorsSort = Query(...),
                   search: str = None,
                   brand:str=None,
                   offset:int=0):
    #strValid(brand)
    return api.getChannels(sort,search,brand,offset)

@app.get('/api/movies',tags=['Movies'])
async def movies(sort: ScenesSort = Query('title'),
                search:str=None,
                tagId:Union[int,str]=None,
                collectionId:Union[int,str]=None,
                actorId:Union[int,str]=None,
                brand:Union[int,str]=None,
                offset:int=0):
    intValid(tagId)
    intValid(collectionId)
    intValid(actorId)
    #strValid(brand)
    return api.getMovies(sort,search,tagId,collectionId,actorId,brand,offset)

@app.get('/api/movies/{movieId}',tags=['Movies'])
async def movie(movieId:int):
    return api.getMovie(movieId)

@app.get('/api/series',tags=['Series'])
async def series(sort: ScenesSort = Query('title'),
                search:str=None,
                tagId:Union[int,str]=None,
                collectionId:Union[int,str]=None,
                actorId:Union[int,str]=None,
                brand:Union[int,str]=None,
                offset:int=0):
    intValid(tagId)
    intValid(collectionId)
    intValid(actorId)
    #strValid(brand)
    return api.getSeries(sort,search,tagId,collectionId,actorId,brand,offset)

@app.get('/api/serie/{serieId}',tags=['Series'])
async def serie(serieId:int):
    return api.getSerie(serieId)

@app.put('/api/settings',tags=['Settings'])
async def appSettings(new_settings: SettingsModel):
    updates = new_settings.dict(exclude_unset=True)

    # Merge updates into the settings
    for key, value in updates.items():
        if isinstance(value, dict) and key in settings:
            settings[key].update(value)  # Update nested dictionaries
        else:
            settings[key] = value

    saveSettings(settings)
    return {"message": "Settings updated successfully", "settings": settings}


@app.get('/web/index')
async def index(request: Request):
    if api.AuthOK==True:
        api_msg=None
    else:
        api_msg=api.expMsg
    
    return templates.TemplateResponse(
        request=request, name="index.html", context={'settings':settings,'msg':api_msg,'k':api.TokenData,'expiry':api.getExpiryTime.strftime('%d-%m-%Y %I:%M %p')}
    )

@app.get('/web/scenes',tags=['Scenes'])
async def webScenes(request:Request,
                    sort:str=settings['sort']['scenes'],
                    search:str=None,
                    tagId:Annotated[List[int],Query()] = None,
                    sceneId:Annotated[List[int],Query()] = None,
                    collectionId:Annotated[List[int],Query()] = None,
                    actorId:Annotated[List[int],Query()] = None,
                    brand:Annotated[List[str],Query()] = None,
                    page:int=1):
    offset=offsetCalc(page, settings['limit'])
    resp=await scenes(sort,search,mergeParams(tagId),mergeParams(sceneId),mergeParams(collectionId),mergeParams(actorId),brand,offset=offset)
    pg=retPaginate('/web/scenes', page, getTotalPages(resp['meta']['total'], settings['limit']),sort=sort,search=search,tagId=tagId,sceneId=sceneId,collectionId=collectionId,actorId=actorId,brand=brand)
    #filters=api.getSceneFilters(mergeParams(tagId),mergeParams(collectionId))
    defval={'search':search,'sort':sort,'brand':brand,'channels':collectionId,'tags':tagId,'actors':actorId,'actorNames':await actor(actorId=mergeParams(actorId)) if actorId else None}
    context={'settings':settings,'scenes':resp['result'],'meta':resp['meta'],'sites':sites,'pg':pg,'sort':sort,'defVal':defval,'sorts':ScenesSortList,'filters':scnFilters}
    return templates.TemplateResponse(request=request, name="allScenes.html", context=context)

@app.get('/web/scene/{sceneId}',tags=['Scenes'])
async def webScene(request:Request,sceneId:int=None):
    fetchScene=api.getScene(sceneId)

    #if fetchScene!=[{'code': 2000, 'message': 'Resource Not Found.'}]:
    if err2k(fetchScene)==True:
        maxRes,trailers=retTrailer(fetchScene['result'])
        print(maxRes,trailers)
        isParent=parentChk(fetchScene)
        downLinks=[]
        try:
            '''Changes Due to EndPoint Response Format Change'''
            #if fetchScene['result']['videos']['full']['files']['320p']['multiCdnId']=='standardScenesCdn':
            if vidChk(fetchScene['result']):
                vids=fetchScene['result']['videos']['full']['files']
                for qu in vids:
                    #downLinks[qu]=vids['format']
                    #downLinks[qu]['sizeBytes']=GetHumanReadable(vids[qu]['sizeBytes'])
                    #downLinks[qu]['urls']['download']=downLinks[qu]['urls']['view'].replace('prog-','download-')+downname(scene,qu)
                    downLinks.append({'format':qu['format'],
                                      'sizeBytes':GetHumanReadable(qu['sizeBytes']),
                                      'view':qu['urls']['view'],
                                      'codec':qu['codec'],
                                      'download':qu['urls']['view'].replace('prog-','download-')+downname(fetchScene['result'],qu['format'])})
                    #print(downLinks)
        except (TypeError,KeyError):
            downLinks=None
    else:
        #downLinks=None
        #isParent=None
        return templates.TemplateResponse(request=request,name="error.html",context={})

    if isParent!=None:
        scenesQ = await scenes(sort='title',sceneId=mergeParams(isParent['sceneIds']))
    else:
        scenesQ=None
    context={'scene':fetchScene['result'],'settings':settings,'downLinks':downLinks,'fetch':fetchScene,'scenePart':isParent,'scenes':scenesQ,'trailers':trailers}
    return templates.TemplateResponse(request=request, name="bySceneId.html", context=context)

@app.get('/web/actors',tags=['Actors'])
async def webActors(request:Request,
                    sort:ActorsSort = Query(settings['sort']['actors']),
                    search:str=None,
                    gender:GenderSort = Query(settings['sort']['gender']),
                    letter:Annotated[List[str],Query()] = None,
                    tagId:Annotated[List[int],Query()] = None,
                    collectionId:Annotated[List[int],Query()] = None,
                    actorId:Annotated[List[int],Query()] = None,
                    brand:Annotated[List[str],Query()] = None,
                    page:int=1):
    offset=offsetCalc(page, settings['limit'])
    gender=gender.value
    sort=sort.value
    resp=await actors(sort,search,gender,mergeParams(letter),mergeParams(tagId),mergeParams(collectionId),mergeParams(actorId),brand,offset=offset)
    pg=retPaginate('/web/actors', page, getTotalPages(resp['meta']['total'], settings['limit']),sort=sort,search=search,tagId=tagId,letter=letter,gender=gender,collectionId=collectionId,actorId=actorId,brand=brand)
    #print(gender)
    #filters=api.getActorFilters(mergeParams(collectionId),mergeParams(tagId),gender,mergeParams(letter))
    defval={'search':search,'sort':sort,'brand':brand,'channels':collectionId,'tags':tagId,'actors':actorId,'letter':letter,'gender':gender}
    context={'settings':settings,'actors':resp['result'],'meta':resp['meta'],'sites':sites,'pg':pg,'sort':sort,'defVal':defval,'sorts':ActorsSortList,'filters':actFilters,'genders':GendersSortList}
    return templates.TemplateResponse(request=request, name="allActors.html", context=context)

@app.get('/web/actor/{actorId}',tags=['Actors'])
async def webActor(request:Request,actorId:int):
    resp = await actor(actorId)
    return templates.TemplateResponse(request=request, name="byActorId.html", context={'actor':resp['result'],'settings':settings})

@app.get('/web/channels',tags=['Channels'])
async def webChannels(request:Request,
                      sort: str=settings['sort']['actors'],
                      search:str=None,
                      brand:Annotated[List[str],Query()] = None,
                      page:int=1):
    offset=offsetCalc(page, settings['limit'])
    resp =await channels(sort,mergeParams(search),brand,offset)
    pg=retPaginate('/web/channels', page, getTotalPages(resp['meta']['total'], settings['limit']),sort=sort,brand=brand)
    defval={'sorts':ActorsSortList,'brand':brand}
    context={'defVal':defval,'sort':sort,'settings':settings,'pg':pg,'channels':resp['result'],'meta':resp['meta'],'sites':sites}
    return templates.TemplateResponse(request=request,name="allChannels.html",context=context)


@app.get('/web/movies',tags=['Movies'])
async def webMovies(request:Request,
                    sort: str = 'title',
                    search:str=None,
                    tagId:Annotated[List[int],Query()]=None,
                    collectionId:Annotated[List[int],Query()]=None,
                    actorId:Annotated[List[int],Query()]=None,
                    brand:Annotated[List[str],Query()]=None,
                    page:int=1):
    offset=offsetCalc(page, settings['limit'])
    resp=await movies(sort,search,mergeParams(tagId),mergeParams(collectionId),mergeParams(actorId),brand,offset)
    pg=retPaginate('/web/movies', page,  getTotalPages(resp['meta']['total'], settings['limit']),sort=sort,search=search,tagId=tagId,collectionId=collectionId,actorId=actorId,brand=brand)
    defval={'search':search,'tagId':tagId,'collectionId':collectionId,'actorId':actorId,'brand':brand}
    context={'settings':settings,'movies':resp['result'],'meta':resp['meta'],'sites':sites,'pg':pg,'sort':sort,'defVal':defval,'sorts':ScenesSortList,'channels':scnFilters['sceneChannels']}
    return templates.TemplateResponse(request=request, name="allMovies.html", context=context)

@app.get('/web/movie/{movieId}',tags=['Movies'])
async def webMovie(request:Request,movieId:int):
    resp = await movie(movieId)
    scIds=[i['id'] for i in resp['result']['children'] if i['type']=='scene']
    mvs = await scenes(sort='title',sceneId=mergeParams(scIds))
    context={'scenes':mvs['result'],'movie':resp['result'],'settings':settings}
    return templates.TemplateResponse(request=request, name="byMovieId.html",context=context)


@app.get('/web/series',tags=['Series'])
async def webSeries(request:Request,
                    sort: str = 'title',
                    search:str=None,
                    tagId:Annotated[List[int],Query()]=None,
                    collectionId:Annotated[List[int],Query()]=None,
                    actorId:Annotated[List[int],Query()]=None,
                    brand:Annotated[List[str],Query()]=None,
                    page:int=1):
    offset=offsetCalc(page, settings['limit'])
    resp=await series(sort,search,mergeParams(tagId),mergeParams(collectionId),mergeParams(actorId),brand,offset)
    pg=retPaginate('/web/series', page,  getTotalPages(resp['meta']['total'], settings['limit']),sort=sort,search=search,tagId=tagId,collectionId=collectionId,actorId=actorId,brand=brand)
    defval={'search':search,'tagId':tagId,'collectionId':collectionId,'actorId':actorId,'brand':brand}
    context={'settings':settings,'series':resp['result'],'meta':resp['meta'],'sites':sites,'pg':pg,'sort':sort,'defVal':defval,'sorts':ScenesSortList,}
    return templates.TemplateResponse(request=request, name="allSeries.html", context=context)

@app.get('/web/serie/{serieId}',tags=['Series'])
async def webSerie(request:Request,serieId:int):
    resp = await serie(serieId)
    scIds=[i['id'] for i in resp['result']['children'] if i['type']=='scene']
    srs = await scenes(sort='title',sceneId=mergeParams(scIds))
    context={'scenes':srs['result'],'serie':resp['result'],'settings':settings}
    return templates.TemplateResponse(request=request, name="bySeriesId.html",context=context)

@app.get('/web/settings',tags=['Settings'])
async def webSettings(request:Request):
    return templates.TemplateResponse(request=request, name="settings.html",context={'settings':settings,
                                                                                     'actorsSort':ActorsSortList,
                                                                                     'scenesSort':ScenesSortList,
                                                                                     'gendersSort':GendersSortList})


@app.post('/api/auth',tags=['Authorization'])
async def setAuthCode(auth:str = Form(...),expiry:int=Form(...)):
    #print(auth)
    #print(expiry)
    o=api.SetAuth(auth,expiry,save=True)
    if o==True:
        print(api.getExpiryTime.isoformat())
        return {'detail':'Authorization has been Set.'}
    else:
        raise HTTPException(status_code=401, detail=f"Invalid Credentials. please retry with correct Credentials")
