import csv
from os.path import dirname,join
import pandas as pd
import random

if __name__ == '__main__':
    postID=input()
    _dir = join(dirname(__file__), '../output/simq-keywords-new/askubuntu/')
    labeled=join(dirname(__file__), '../data/labeled/askubuntu.csv')
    clarq = join(dirname(__file__), '../data/clarq/askubuntu.csv')
    tags_csv=join(_dir, 'keywords_unclear_id.csv')
    body_csv = join(_dir, 'keywords_unclear_id_body.csv')
    df_tags=pd.read_csv(tags_csv)
    df_body=pd.read_csv(body_csv)
    df_post=pd.read_csv(labeled)
    df_qs=pd.read_csv(clarq)
    while(True):
        try:
            length=len(df_tags.query('id==' + postID).values[0])
            break
        except Exception as e:
            postID=str(int(postID)+1)
    list_tags=df_tags.query('id=='+postID).values
    list_body=df_body.query('id=='+postID).values

    #title+tags
    tags_scores=[]
    for i in list_tags:
        item0=str(i)
        item=item0.split(" ")
        tags_scores.append(item[-2])
    index=-1
    result=0
    for s in tags_scores:
        index+=1
        if s==max(tags_scores):
            result=list_tags[index]
            break
    keywords=result[1]
    simID=result[3]
    print(postID)
    title=df_post.query('id==' + postID).values[0][1]
    clarq=df_qs.query('id==' + str(simID)).values[0][1]
    #body
    body_ids=[]
    for i in list_body:
        item1=str(i[-1])
        body_ids.append(item1)
    random_ids = random.sample(body_ids, 3)
    clarq_body=[]
    for id in random_ids:
        clarq_body.append(df_qs.query('id==' + str(id)).values[0][1])

    output_txt=join(dirname(__file__), 'pred_{}.txt'.format(postID))
    with open(output_txt, 'w', newline='') as file:
        file.write(postID+"\n")
        file.write("Title: "+title+"\n")
        file.write("Clarq_rake: "+clarq+"\n")
        file.write("keywords: "+keywords+"\n")
        file.write("Clarq_body: "+"\n")
        file.write(clarq_body[0]+"\n"+clarq_body[1]+"\n"+clarq_body[2])