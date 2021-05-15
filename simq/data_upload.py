import get_community,get_words,find_similar
import os
from itertools import chain
import elasticsearch
import elasticsearch.helpers
import numpy as np

INDEX_SETTINGS = {
    "settings": {
        "similarity": {
            "my_bm25": {
                "type": "BM25",
                "b":    0.75,
                "k1": 1.2
            }
        }
    },
    "mappings": {
        "post": {
            "_all": {
                "enabled": False
            },
            "properties": {
                "title": {
                    "type": "string",
                    "analyzer": "stop",
                    "similarity": "my_bm25"
                },
                "body": {
                    "type": "string",
                    "analyzer": "stop",
                    "similarity": "my_bm25"
                },
                "tags": {
                    "type": "string",
                    "analyzer": "stop",
                    "similarity": "my_bm25"
                },
                "combined": {
                    "type": "string",
                    "analyzer": "stop",
                    "similarity": "my_bm25"
                },
                "label": {
                    "type": "string",
                    "analyzer": "whitespace",
                }
            }
        }
    }
}

es_host = os.getenv('ELASTIC_HOST', '127.0.0.1')
es_port = os.getenv('ELASTIC_PORT', '9200')
es = elasticsearch.Elasticsearch(['http://{}:{}'.format(es_host, es_port)])


def get_post_document(post, post_id, label):
    title, body, tags = post[0], post[1], post[2]

    title = get_words.get_words(title)
    body = get_words.get_words(body)
    tags = get_words.get_words(tags)

    return {
        '_id': str(post_id),
        'title': ' '.join(title),
        'body': ' '.join(body),
        'tags': ' '.join(tags),
        'combined': ' '.join(title + body + tags),
        'label': label
    }

def get_actions(index_name, doc_type, posts, labels, post_ids):
    for post, post_id, label in zip(posts, post_ids, labels):
        yield {
            '_op_type': 'index',
            '_index': index_name,
            '_type': doc_type,
            **get_post_document(post, post_id, label)
        }

def main(args):
    X_train, y_train, train_ids, X_test, test_ids = get_community.load_labeled(args['community'])
    index_name = '{}_unclear'.format(args['community'])
    print("Start indexing posts into elasticsearch.")

    #get unclear posts from all posts
    unclear_ixs = np.where(y_train == 1)[0]
    X_train = np.take(X_train, unclear_ixs, axis=0)
    y_train = np.take(y_train.values, unclear_ixs, axis=0).tolist()
    train_ids = np.take(train_ids, unclear_ixs, axis=0).tolist()

    #upload unclear data
    actions = get_actions(index_name, "post", X_train, y_train, train_ids)
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name, body=INDEX_SETTINGS)
    for ok,response in elasticsearch.helpers.streaming_bulk(es,actions):
        if  not ok:
            print(response)
    total = len(train_ids) +len(test_ids)
    def posts(): return chain(X_train, X_test)
    def ids(): return chain(train_ids, test_ids)

    #get similar posts
    find_similar.find(args,es,index_name,args['run_id'],posts(),ids(),total)


if __name__ == '__main__':
    args = {
        'community': "askubuntu",
        'run_id': "sim_cal_body",
        'strategy': "body_only",
        'debug': False,
        'body_length': 100,
    }

    main(args)
