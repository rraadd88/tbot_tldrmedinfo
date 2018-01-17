from os import makedirs
from os.path import exists,basename
import subprocess

def get_healthpng(searchstr='dengue'):
    from selenium import webdriver
    browser = webdriver.Chrome()
    browser.get('https://www.google.co.in/search?q={}&num=1'.format(searchstr))
    html_source = browser.page_source
    browser.close()

    inistr='https://g.co/healthpdf/'
    endstr='_en_IN.pdf'
    ini=html_source.find(inistr)
    end=html_source.find(endstr)+len(endstr)
    lnk_healthpdf=html_source[ini:end]
    
    data_lnk='data'
    if not exists(data_lnk):
        makedirs(data_lnk)
    if lnk_healthpdf!='':
        lnk_healthpdf_png='{}/{}'.format(data_lnk,basename(lnk_healthpdf).replace('.pdf','.png'))
        if not exists(lnk_healthpdf_png):
#             lnk_healthpdf='data/anemia_en_IN.pdf'
            com='cd data;wget {}; convert -trim -quality 100 -density 150 -gravity center -crop 700x1330-70+25 {} {}_pages_%02d.png; convert {}_pages_*.png -trim -append {}; cd -;'.format(lnk_healthpdf,
                                                        basename(lnk_healthpdf),
                                                        basename(lnk_healthpdf).replace('.pdf',''),
                                                        basename(lnk_healthpdf).replace('.pdf',''),
                                                        basename(lnk_healthpdf).replace('.pdf','.png'))
            subprocess.call(com,shell=True)
            subprocess.call(com,shell=True)
        return lnk_healthpdf_png
    else:
        return None

import tweepy
def auth(params_auth):
    auth = tweepy.OAuthHandler(params_auth['consumer_key'], params_auth['consumer_secret'])
    auth.set_access_token(params_auth['access_token'], params_auth['access_token_secret'])
    api = tweepy.API(auth,wait_on_rate_limit=True)
    return api
def send_twit(api,line,img_lnk=None):
    if img_lnk is None:
        metadata=api.update_status(line)
    else:
        metadata=api.update_with_media(img_lnk,status=line)
    return metadata

def simplify_twit(twit_text):
    import nltk
    import string
    from nltk.corpus import stopwords
    words_common=set(stopwords.words('english'))
    words_del=['rt']

    twit_words=twit_text.lower().split()
    twit_words=[s for s in twit_words if not 'https' in s]
    twit_words=[s for s in twit_words if not '@' in s]
    for p in string.punctuation:
        twit_words=[s.replace(p,'') for s in twit_words]
    twit_words=[s for s in twit_words if not s in words_del]        
    twit_words=list(filter(lambda w: not w in words_common,twit_words))
    twit_words_tagged = nltk.pos_tag(twit_words)
    twit_words=[word for word,typ in twit_words_tagged if typ.startswith('NN')]
    return ' '.join(twit_words)

def send_healthpng(api,status):
    print('{} : {}'.format(status.id,status.text))
    status_text=status.text.lower()
    filter_exclude=['trump','hillary']
    if sum([True for flt in filter_exclude if flt in status_text])==0:            
        if '@tldrmedinfo' in status_text:
            if status_text.startswith('@tldrmedinfo'):
                search_kw=status_text.split('@tldrmedinfo ')[1]
        elif 'symptoms of' in status_text:
            search_kw=simplify_twit(status_text)
        print(search_kw)
        img_lnk=get_healthpng(searchstr=search_kw) 

    if not img_lnk is None: 
        media_ids = [api.media_upload(i).media_id_string for i in [img_lnk]]
        status_data=api.update_status(status='@{} FYI'.format(status.user.screen_name),
                                     in_reply_to_status_id=status.id_str,
                                     media_ids=media_ids)
        print('replied: {}'.format(img_lnk))
    elif 'creator' in search_kw:
        status_data=api.update_status(status='@{} @rraadd88.'.format(status.user.screen_name),
                                     in_reply_to_status_id=status.id_str)
        print('creator')
    else:
        print('img_lnk is None')
