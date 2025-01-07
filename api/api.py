import requests as req
import json
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

class AiloLite():
    def __init__(self):
        self.__headers = {#"cookie": "__s=65FEF506-42FE72EA01BB31199D-5047",
        "User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.3",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        "Instance": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJtaW5kZ2VlayIsImF1ZCI6Im1pbmRnZWVrIiwic3ViIjoiaW5zdGFuY2UtYXBpIiwiZXhwIjoxNzMxNTQyNDAwLCJpZCI6MjMyMjMxLCJicmFuZCI6InJlYWxpdHlraW5ncyIsImhvc3RuYW1lIjoic2l0ZS1tYS5yZWFsaXR5a2luZ3MuY29tIn0.WpHiFTmx582dLuENWcW_kfElPYogoXPhr9i1mxmoG0Q"
        }
        #self._metas=list(self._instances.keys())
        #self._groups=json.load(open('groups-2.json','r'))
        self._groups=None
        self.__AllGrps=None
        self.loadGrps()
        self.__useProxy=False
        self.__resLim=100
        self.__MaxThreads=6
        self.__url = "https://site-api.project1service.com/"
        self.__modSort={'alpha':"name",'rating':"-stats.rating",'lastScene':"-lastSceneReleaseDate",
                        'mostViews':"-stats.views","mostVideos":"-stats.scenes"}
        self.__vidSort={'date':'-dateReleased','rating':'-stats.rating','views':'-stats.views','title':'title','likes':'-stats.likes'}
        self.__colSort={'lastScene':"-lastSceneReleaseDate",'alpha':"name"}
        self.__proxy={'http': 'socks5://127.0.0.1:9050','https': 'socks5://127.0.0.1:9050'}
        self.__date=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
        self.__AOk=False
        self.__exp=None
        self.__tdata=None
        self.expMsg="Auth Expired. Please Renew."
        self.__h=5
        self.__m=30

    @property
    def instances(self):
        return self.__headers['Instance']
        
    @property
    def resultLimit(self):
        return self.__resLim

    @resultLimit.setter
    def resultLimit(self,num:int):
        if num>100:
            raise ValueError("result limit should not be more than 100.")
        else:
            self.__resLim=num

    @property
    def AllGrps(self):
        return self.__AllGrps

    def loadGrps(self):
        self._groups=json.load(open('sites.json','r'))
        self.__AllGrps=';'.join([self._groups[i]['ids'] for i in self._groups if self._groups[i]['show']==True])

    def SetAuth(self,auth,expiry,save=False):
        self.__headers['Authorization']=auth
        #t=self.Test()
        self.__exp=expiry
        '''
        try:
            if t[0]['message']=='Authentication Failed.':
                self.__headers['Authorization']=None
                return False
        except KeyError:
            self.__AOk=True
            self.__tdata=t
            if save==True:
            '''
        if self.isExpired==False:
            with open('auth.json','w') as wf:
                json.dump({'Auth':auth,'Inst':self.__headers['Instance'],'Expiry':expiry},wf,indent=4)
            wf.close()
            return True
        return False
    @property
    def isExpired(self):
        t=self.Test()
        try:
            if t[0]['message']=='Authentication Failed.':
                self.ExpireAuth()
                self.__headers['Authorization']=None
                return True
        except KeyError:
            self.__AOk=True
            self.__tdata=t
            return False

    def SetTimeZone(self,h:int,m:int):
        self.__h=h
        self.__m=m

    def loadFromFile(self):
        data=json.load(open('auth.json','r'))
        return self.SetAuth(data['Auth'],data['Expiry'])

    def ExpireAuth(self):
        self.__AOk=False
        self.__tdata=None

    @property
    def AuthOK(self):
        return self.__AOk

    @property
    def nowTime(self):
        return datetime.now().replace(second=0,microsecond=0)

    @property
    def getExpiryTime(self):
        if self.__exp==None:
            return datetime.now()
        else:
            return (datetime.utcfromtimestamp(self.__exp)+timedelta(hours=self.__h,minutes=self.__m)).replace(second=0,microsecond=0)

    @property
    def TokenData(self):
        return self.__tdata
            
    def __fet(self,url,params):
        #self.__headers['instance']=self.instances[meta]
        #print(url)
        #print(self.__headers)
        #print(params)
        params['limit']=self.__resLim
        return req.get(url,headers=self.__headers,params=params).json()
    
    @staticmethod
    def copy(a,ttl):
        for i in range(1,ttl):
            yield a

    def __allFet(self,url,query=dict()):
        query=query|{'limit':self.__resLim,'offset':0}
        print(query)
        p1=self.__fet(url,query)
        #print(p1)
        if p1['meta']['total']==0:
            return p1
        ttl=int(-1 * (p1['meta']['total']/p1['meta']['count']) // 1 * -1)
        res=[]
        res.extend(p1['result'])
        queries=[query|{'offset':i*self.__resLim} for i in range(1,ttl)]
        #print(ttl)
        with ThreadPoolExecutor(max_workers=self.__MaxThreads) as executor:
            for i in list(executor.map(self.__fet,self.copy(url,ttl),queries)):
                res.extend(i['result'])
        return {'total':len(res),'result':res}

    def getGrps(self,vals):
        if vals!=None:
            return ';'.join([self._groups[i]['ids'] for i in self._groups if i in vals])
        return self.__AllGrps

    def Test(self):
        #return self.__fet({'page':'self','ver':'v1'})
        return self.__fet(f'{self.__url}v1/self',{})

    def getSceneFilters(self,tagId:int=None,collectionId:int=None):
        q={"dateReleased":'<'+self.__date,"type":"scene",'groupId':self.AllGrps}
        if tagId: q['tagId']=tagId
        if collectionId: q['collectionId']=collectionId
        return self.__fet(self.__url+'v2/release-filters',q)
        
    def getScenes(self,sort:str='date',search:str=None,tagId:int=None,sceneId:int=None,collectionId:int=None,actorId:int=None,brand:str=None,offset:int=0):
        if sort in self.__vidSort:
            q={"adaptiveStreamingOnly":False,
               "dateReleased":'<'+self.__date,
               "orderBy":self.__vidSort[sort],
               "type":"scene",
               "groupId":self.getGrps(brand),
               "offset":offset}
            if search: 
                q['search']=search
                q['orderBy']='-relevance'
            if tagId: q['tagId']=tagId
            if collectionId: q['collectionId']=collectionId
            if sceneId: q['id']=sceneId
            if actorId: q['actorId']=actorId
            return self.__fet(self.__url+'v2/releases',q)
        else:
            raise ValueError(f'No Sort as "{sort}" is defined.')

    def getScene(self,sceneId:int):
        return self.__fet(f'{self.__url}v2/releases/{sceneId}',{})
        
    def getActors(self,sort:str='alpha',search:str=None,gender:str=None,letter:str=None,tagId:int=None,collectionId:int=None,actorId:int=None,brand:int=None,offset:int=0):
        if sort in self.__modSort:
            q={'lastSceneReleaseDate':'<'+self.__date,
               'orderBy':self.__modSort[sort],
               "groupId":self.getGrps(brand),
               'offset':offset}
            if tagId: q['tagId']=tagId
            if collectionId: q['collectionId']=collectionId
            if actorId: q['id']=actorId
            if search: 
                q['search']=search
                q['orderBy']='-relevance'
            if gender and gender!='all': 
                q['gender']=gender
            if letter: q['letter']=letter

            return self.__fet(self.__url+'v1/actors',q)
        else:
            raise ValueError(f'No Sort as "{sort}" is defined.')

    def getActorFilters(self,collectionId:int=None,tagId:int=None,gender:str=None,letter:str=None):
        q={'groupId':self.AllGrps}
        if collectionId: q['collectionId']=collectionId
        if tagId: q['tagId']=tagId
        if gender and gender!='all': 
                q['gender']=gender
        if letter: q['letter']=letter
        return self.__fet(self.__url+'v2/actor-filters',q)

    def getActor(self,actorId):
        return self.__fet(f'{self.__url}v1/actors/{actorId}',{})

    def getGroups(self):
        return self.__fet(self.__url+'v2/groups',{})

    def getChannels(self,sort:str='alpha',search:str=None,brand:int=None,offset:int=0):
        if sort in self.__modSort:
            q={'offset':offset,'orderBy':self.__colSort[sort],'groupId':self.getGrps(brand)}
            if search: 
                q['search']=search
                q['orderBy']='-relevance'
            return self.__fet(self.__url+'v1/collections/',q)
        else:
            return ValueError(f'No Sort as "{sort}" is defined.')

    def getMovies(self,sort:str='title',search:str=None,tagId:int=None,collectionId:int=None,actorId:int=None,brand:str=None,offset:int=0):
        q={"groupId":self.getGrps(brand),"orderBy":self.__vidSort[sort],"dateReleased":'<'+self.__date,"offset":offset,"type":"movie"}
        if sort in self.__vidSort:
            if search: 
                q['search']=search
                q['orderBy']='-relevance'
            if tagId: q['tagId']=tagId
            if collectionId: q['collectionId']=collectionId
            if actorId: q['actorId']=actorId
            return self.__fet(self.__url+'v2/releases', q)

    def getMovie(self,movieId):
        q={'groupId':self.AllGrps,'type':'movie'}
        return self.__fet(self.__url+f'v2/releases/{movieId}', q)

    def getSeries(self,sort:str='title',search:str=None,tagId:int=None,collectionId:int=None,actorId:int=None,brand:str=None,offset:int=0):
        q={"groupId":self.getGrps(brand),"orderBy":self.__vidSort[sort],"dateReleased":'<'+self.__date,"offset":offset,"type":"serie"}
        if sort in self.__vidSort:
            if search: 
                q['search']=search
                q['orderBy']='-relevance'
            if tagId: q['tagId']=tagId
            if collectionId: q['collectionId']=collectionId
            if actorId: q['actorId']=actorId
            return self.__fet(self.__url+'v2/releases', q)

    def getSerie(self,serieId):
        q={'groupId':self.AllGrps,'type':'serie'}
        return self.__fet(self.__url+f'v2/releases/{serieId}', q)
        
    def AllTags(self):
        q={'groupId':self.AllGrps}
        return self.__allFet(self.__url+'v1/tags',q)
