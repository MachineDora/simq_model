from os.path import dirname,join
import get_words
import os
from tqdm import tqdm
import requests
import json

def query_text(args, post):
    title, body, tags = post[0], post[1], post[2]
    title = get_words.get_words(title)
    tags = get_words.get_words(tags)

    query = ''
    #only title and tags
    if args['strategy'] == 'constrained':
        query = ' '.join(title + tags)
    #title tags and body
    elif args['strategy'] == 'all':
        body = get_words.get_words(body)
        # remove excessively long tokens (e.g. stack dumps on unix)
        body = [token for token in body if len(token) <= 40]
        body = body[:args['body_length']]
        query = ' '.join(title + body + tags)
    elif args['strategy'] == 'body_only':
        body = get_words.get_words(body)
        # remove excessively long tokens (e.g. stack dumps on unix)
        body = [token for token in body if len(token) <= 40]
        body = body[:args['body_length']]
        query=' '.join(body)
    else:
        raise ValueError('Unknown query strategy "{}"'.format(args['strategy']))

    return query

def find(args, es, index_name, run_id, posts, ids, total):
    simq_path = join(dirname(__file__), '../../output/simq/')
    simq_file = join(simq_path, '{}_{}_all.txt'.format(index_name, run_id))
    os.makedirs(simq_path, exist_ok=True)
    with open(simq_file, 'w') as run_file:
        for post, post_id in tqdm(zip(posts, ids), total=total):
            query = query_text(args, post)
            to_search_html="http://localhost:9200/"+index_name+"/_search?q=combined:"+query#转为用网页遍历查询
            try:
                r = requests.get(to_search_html)
                hits = json.loads(str(r.text))['hits']['hits']
                for i, hit in enumerate(hits):
                    run_file.write('{} Q0 {} {} {} {}\n'.format(
                        post_id, hit['_id'], i, hit['_score'], run_id))
            except Exception as e:
                print('Exception during querying of post "%s"', post_id)