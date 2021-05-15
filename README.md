运行顺序：
data_upload: 上传数据并寻找相似posts
rake_keywords: 使用rake提炼关键词
generate_sentences: 生成第一阶段的输出，作为模型2的输入

运行环境：
python=3.5
elasticsearch=2.3
numpy=1.13.1
tqdm=4.23.4
request=2.25.1
pandas=0.23.1
scikit-learn=0.19.1
spicy=1.1.0
