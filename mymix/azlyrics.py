import numpy as np
import urllib3
from bs4 import BeautifulSoup



http = urllib3.PoolManager()

def strip_off_punc(string):
        
    punctuations = '''!()-[]{};:'"\,<>./?~'''
    no_punct = ""
    for char in string:
       if char not in punctuations:
           no_punct = no_punct + char
    
    return no_punct

def remove_the(string):
    if string.lower().startswith("the"):  
        return string[3:].strip()
    else:
        return string

def all_versions(track_name,track_artistname):

    
    track_name = remove_the(track_name)
    track_artistname = remove_the(track_artistname)


    
    original_artistname = original_artist(track_artistname,track_name)
    
    

    if original_artistname:
        track_artistname =   original_artistname

    
    domain = 'https://search.azlyrics.com/search.php'
    query_url = '?q=' + track_name + '+' + track_artistname
    url = domain + query_url
    

    
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)
    
    page_box = soup.findAll('a', {"class": "btn btn-share btn-nav"},href=True)
    
    
    page_links = []
    for link in page_box:
        page_links.append(link.get('href'))
    page_links = set(page_links)
    page_links = [url + '&w=songs&p=1'] + [ domain + p for p in page_links ]

    

    
    text = []
    for p_link in page_links:
        
        response = http.request('GET', p_link)
        soup = BeautifulSoup(response.data)
        box = soup.findAll("td", {"class": "text-left visitedlyr"})
        
        for td in box:
            bs = td.findAll('b')
            for b in bs:
    
                text.append(b.text.strip().lower())
        
    try:
        matched_label=[]
        data = np.array(text).reshape((-1,2))
        
        for i, d in enumerate(data[:,0]):
            
            if remove_the(d) == track_name.lower():
            
                matched_label.append(i)
        

        matched_data = data[matched_label]
        artistnames = set(matched_data[:,1])

        return artistnames
    except:
        return {}




def artist_filter(query):

    stopwords = ['originally','by','cover']
    querywords = strip_off_punc(query).split()
    
    resultwords  = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)

    return result


# def get_lyrics_url(artist,song_title):
#     url = 'https://search.azlyrics.com/search.php?q=' +  song_title + '+' + artist 
#     response = http.request('GET', url)
#     soup = BeautifulSoup(response.data)
#     td = soup.find("td", {"class": "text-left visitedlyr"})
#     try:
#         link = td.find('a',href=True)
#         return link.get('href')
#     except:
#         return ""
    

# def original_artist(artist,song_title):

#     url = get_lyrics_url(artist,song_title)
#     response = http.request('GET', url)
#     soup = BeautifulSoup(response.data)
#     try:
#         original = soup.find('span', {"class": "feat"}).text
#         return artist_filter(original)
    
#     except:
#         return None

def get_lyrics_url(artist,song_title):
    url = 'https://search.azlyrics.com/search.php?q=' +  song_title + '+' + artist 
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data)
    td = soup.find("td", {"class": "text-left visitedlyr"})
    try:
        link = td.find('a',href=True)
        return link.get('href')
    except:
        return "not sure {} have covered  {}...".format(artist,song_title)

    

def original_artist(artist,song_title):
    try:
        url = get_lyrics_url(artist,song_title)
        if url[:4]!= 'http':
            return url
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data)

        original = soup.find('span', {"class": "feat"}).text
        return artist_filter(original)
    
    except:
        return None


def get_lyrics(url):
    
    try:
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data)
        lyrics = str(soup)
        # lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('</div>','').strip()
        return lyrics
    except Exception as e:
        return "Exception occurred \n" +str(e)