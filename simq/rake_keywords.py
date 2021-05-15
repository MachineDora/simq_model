import os
import csv
import get_community,get_words,rake
import itertools
from collections import Counter, defaultdict
from os.path import dirname, join
from scipy import spatial
import numpy as np

def load_sim(file):
    #use dict to save the mapping data
    ids = defaultdict(list)
    scores = defaultdict(list)
    with open(file) as f:
        for line in f:
            (qid, _, doc_id, _, score, _) = line.strip().split()
            qid, doc_id = int(qid), int(doc_id)
            if qid == doc_id:
                #don't save itself.
                continue
            ids[qid].append(doc_id)
            scores[qid].append(float(score))
    return ids, scores

def run_path(run_id):
    return join(dirname(__file__), '../output/simq', run_id)

def get_question(clarq_comment):
    #get only question
    tokens = get_words.get_words(clarq_comment)
    end = tokens.index('?') + 1
    context = tokens[:end][::-1]

    start = 0
    if '.' in context:
        #remove context
        start = end - context.index('.')

    clarq = tokens[start:end]
    clarq = [token for token in clarq if token.isalpha()]
    return ' '.join(clarq)

def get_post_words(posts, id):
    p = posts.loc[id]
    combined = '{} {} {}'.format(p.title, p.body, p.tags)
    post_words = get_words.get_words(combined)
    return post_words

def to_rake(clarq):
    _rake=rake.Rake()
    chunks = _rake.run(clarq)
    words = [word for chunk, _ in chunks for word in chunk.split()]
    return words

def score_cosine(a, b):
    sim = 1 - spatial.distance.cosine(a, b)
    if np.isnan(sim):
        sim = 0
    return sim

def vectorize_subjects(p, cq):
    #gengerate vectors for p and q
    p_counts = Counter(p)
    subjects = Counter(itertools.chain.from_iterable(cq))
    subject_keys = sorted(subjects.keys())
    p_vec = [p_counts.get(key, 0) for key in subject_keys]
    cq_vec = [subjects.get(key) for key in subject_keys]
    return p_vec, cq_vec

def simBM25_cal(posts,clarqs,p_id,q_ids,q_scores):
    post_words = get_post_words(posts,p_id)
    cq=clarqs.loc[q_ids]['clarification_question'].values
    score = []
    p_cq_subjects = []
    q_idss=[]
    for clarq, weight, q_id in zip(cq, q_scores,q_ids):
        if str(clarq) == "nan":
            clarq = "NoClarQ"
        cq_subjects = to_rake(clarq)
        p_cq_subjects.append(cq_subjects)
        p_vec, cq_vec = vectorize_subjects(post_words, [cq_subjects])
        score.append(score_cosine(p_vec, cq_vec) * weight)
        q_idss.append(q_id)
    return p_cq_subjects, score,q_idss

def main(args):
    #load data and clarq
    df_posts = get_community.load_raw(args['community'])
    df_posts.set_index('id', inplace=True)
    df_clarqs = get_community.load_clarqs(args['community'])
    df_clarqs['clarification_question'] = df_clarqs['clarification_question'].apply(get_question)
    df_clarqs.set_index('id', inplace=True)

    similar_unclear, scores_unclear = load_sim(
        run_path('{}_unclear_{}_body.txt'.format(args['community'], args['run_id'])))
    values = []
    p_ids=df_posts.index.values
    print(len(p_ids))
    i=0
    for p_id in p_ids:
        i+=1
        print(i)
        try:
            q_ids = similar_unclear[p_id][:50]
            q_scores = scores_unclear[p_id][:50]
            values.append(simBM25_cal(df_posts,df_clarqs,p_id, q_ids, q_scores))
        except Exception as e:
            print(e)

    out_path = '../output/simq-keywords-new/{}/'.format(args['community'])
    out_path = join(dirname(__file__), out_path)
    os.makedirs(out_path, exist_ok=True)
    out_file = '{}.csv'.format("keywords_unclear_id_body")
    with open(join(out_path, out_file), 'w',newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id","keywords","simBM25","sim_id"])
        for post_id, value in zip(p_ids, values):
            for i in range(0,len(value[0])):
                writer.writerow([post_id, value[0][i],value[1][i],value[2][i]])

if __name__ == '__main__':
    args = {
        'community': "askubuntu",
        'run_id': "sim_cal",
        'n_jobs': 1
    }
    main(args)