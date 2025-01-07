'''
def paginate_data(total_records: int, limit: int) -> dict:
    # Calculate the total number of pages
    total_pages = (total_records // limit) + (1 if total_records % limit != 0 else 0)
    
    # Initialize a dictionary to store page number and corresponding offset
    pages = {}
    
    # For each page, calculate the offset value
    for page in range(1, total_pages + 1):
        offset = (page - 1) * limit
        pages[page] = offset
    
    # Return the dictionary with the total number of pages and offset values
    return {"total_pages": total_pages, "pages": pages}
'''
def getTotalPages(total_records:int, limit:int) -> int:
    return (total_records // limit) + (1 if total_records % limit != 0 else 0)

def ellipsis(c, m) -> list:
    current = c
    last = m
    delta = 2
    left = current - delta
    right = current + delta + 1
    range_list = []
    range_with_dots = []
    l = None

    for i in range(1, last + 1):
        if i == 1 or i == last or (i >= left and i < right):
            range_list.append(i)

    for i in range_list:
        if l:
            if i - l == 2:
                range_with_dots.append(l + 1)
            elif i - l != 1:
                range_with_dots.append('...')
        range_with_dots.append(i)
        l = i

    return range_with_dots

def offsetCalc(page:int,limit:int):
    return (page - 1) * limit

def retLink(params,url):
    strQ="?"
    for k,v in params.items():
        if type(v)==list and v!=None:
            for i in v:
                strQ += k + '=' + str(i) + "&"
        elif type(v)==str or type(v)==int:
            strQ += k + '=' + str(v) + "&"
    return url+strQ[0:-1]

def retPaginate(url,page,pages,**kwargs):
    #here the kwargs will be used to make url params 
    #print(url)
    #print(kwargs)
    #page=query['page']
    #pages=query['pages']
    #print(query['pages'],query['page'],query['size'])
    ellips=ellipsis(page,pages)
    links=[(i,retLink(kwargs | {'page':i},url)) if i!='...' else (i,'') for i in ellips]
    #np=[query['page']-1,query['page'],query['page']+1]
    toret={'ellipsis':links}
    toret['page']=page

    if pages == 1:
        return toret

    # Check if page number is within valid range
    if page < 1:
        page = 1
    elif page > pages:
        page = pages

    # Determine previous and next page numbers
    #prev_page = page_no - 1 if page_no > 1 else None
    if page>1:
        kwargs.update({'page':page-1})
        toret.update({'prev':retLink(kwargs,url)})

    #next_page = page_no + 1 if page_no < total_pages else None
    if page < pages:
        kwargs.update({'page':page+1})
        toret.update({'next':retLink(kwargs,url)})

    return toret

