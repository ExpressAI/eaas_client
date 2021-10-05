# EaaS_API

## Documentation
Documentation at https://expressai.github.io/EaaS_API_dev/. Some references for writing docs can refer to
- https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer
- https://sphinx-tutorial.readthedocs.io/step-1/
- https://sphinx-themes.org/sample-sites/furo/

## Usage
To install the API, simply run
```bash
pip install eaas
```

To use the API, run the following.

```python
from eaas import Client
client = Client()
client.load_config("config.json")

# To use this API for scoring, you need to format your input as list of dictionary. 
# Each dictionary consists of `source` (string, optional), `references` (list of string, optional) 
# and `hypothesis` (string, required). `source` and `references` are optional based on the metrics 
# you want to use. Please do not conduct any preprocessing on `source`, `references` or `hypothesis`, 
# we expect normal-cased detokenized texts. All the preprocessing steps are taken by the metrics. 
# Below is a simple example.

inputs = [{"source": "This is the source.", 
           "references": ["This is the reference one.", "This is the reference two."],
           "hypothesis": "This is the generated hypothesis."}]
metrics = ["bleu", "chrf"] # Can be None for simplicity if you consider using all metrics

score_dic = client.score(inputs, task="sum", metrics=metrics, lang="en") 
# inputs is a list of Dict, task is the name of task, metrics is metric list, lang is the two-letter code language
```



The output is like
```
# sample_level is a list of dict, corpus_level is a dict
{
    'sample_level': [
        {'bleu': 32.46679154750991,
         'attr_compression': 1.2,
         'attr_copy_len': 2.0,
         'attr_coverage': 0.8,
         'attr_density': 2.0,
         'attr_hypothesis_len': 5,
         'attr_novelty': 0.5,
         'attr_repetition': 0.0,
         'attr_source_len': 6,
         'chrf': 38.56890099861521}
    ],
    'corpus_level': {
        'corpus_bleu': 32.46679154750991,
        'corpus_attr_compression': 1.2,
        'corpus_attr_copy_len': 2.0,
        'corpus_attr_coverage': 0.8,
        'corpus_attr_density': 2.0,
        'corpus_attr_hypothesis_len': 5.0,
        'corpus_attr_novelty': 0.5,
        'corpus_attr_repetition': 0.0,
        'corpus_attr_source_len': 6.0,
        'corpus_chrf': 38.56890099861521
    }
}
```


## Long-term TODO
- [ ] 完善功能
- [ ] 只给aws的ip (起一个api.eaas类似这样的域名)
- [X] 打包成package
- [X] metric corpus-level指标计算; BLEU corpus-level的计算检查（是否其他metric也有类似的）；我们可能要设计下返回结果的json格式
- [ ] 我们弄个文档，总结每个指标的默认预处理方法，超参数使用，考虑是否预留个接口给用户设置
- [ ] Confidence interval计算功能
- [ ] Fine-grained analysis功能
- [ ] 优化API访问效率
