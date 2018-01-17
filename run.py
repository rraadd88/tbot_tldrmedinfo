from modules import auth, send_healthpng
from keys import params_auth
from tmp import since_id
api=auth(params_auth)
# since_id='953680302634758145'
while True:
    twits=api.search(q='@tldrmedinfo',
    #                  lang='en',
                     count=100,
    #                  result_type='recent',
                     since_id=since_id,
                    )
    if len(twits)>0:
        for t in twits:
            if not 'FYI' in t.text: 
                send_healthpng(api,t)
        since_id=twits[0].id
        with open('tmp.py', 'w') as f:
            f.write("since_id='{}'".format(since_id))
