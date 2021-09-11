from typing import List, Dict
import requests
import json
import warnings
from tqdm import trange
from collections import defaultdict
import os
from time import gmtime, strftime

BATCH_SIZE = 100


class Client:
    def __init__(self):
        """ A client wrapper """
        # self.end_point = "http://18.224.144.134/"
        self._record_end_point = "http://piaget.lti.cs.cmu.edu:6666/record"
        self._score_end_point = "http://piaget.lti.cs.cmu.edu:6666/score"
        self._valid_metrics = [
            "bart_score_summ",
            "bart_score_mt",
            "bert_score",
            "bleu",
            "chrf",
            "comet",
            "comet_qe",
            "mover_score",
            "prism",
            "prism_qe",
            "rouge"
        ]
        self._config = None

    def load_config(self, config_file="config.json"):
        assert os.path.exists(config_file), "The config file does not exist."
        with open(config_file, "r") as f:
            config = json.loads(f.read())
        self._config = config

    @property
    def metrics(self):
        return self._valid_metrics

    def log_request(self, inputs, metrics):
        """ Log the metadata of this request. """
        def word_count(l):
            """ count words in a list (or list of list)"""
            c = 0
            for x_ in l:
                if isinstance(x_, List):
                    c += word_count(x_)
                else:
                    c += len(x_.split(" "))
            return c

        srcs = [x["source"] for x in inputs]
        refs = [x["references"] for x in inputs]
        hypos = [x["hypothesis"] for x in inputs]

        srcs_wc = word_count(srcs)
        refs_wc = word_count(refs)
        hypos_wc = word_count(hypos)

        return {
            "date:": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "user": "placeholder",
            "metrics": metrics,
            "src_tokens": srcs_wc,
            "refs_tokens": refs_wc,
            "hypos_tokens": hypos_wc
        }

    def score(self, inputs: List[Dict], metrics=None):
        # assert self._config is not None, "You should use load_config first to load metric configurations."

        if metrics is None:
            metrics = self._valid_metrics
            warnings.warn("You didn't specify the metrics, will use all valid metrics by default.")
        else:
            for metric in metrics:
                assert metric in self._valid_metrics, "Your have entered invalid metric, please check."

        # First record the request
        metadata = self.log_request(inputs, metrics)
        response = requests.post(url=self._record_end_point, json=json.dumps(metadata))
        if response.status_code != 200:
            raise RuntimeError("Internal server error.")
        print(f"Your request has been sent.")

        inputs_len = len(inputs)

        final_score_dic = {}
        # First deal with BLEU and CHRF
        if "bleu" in metrics:
            data = {
                "inputs": inputs,
                "metrics": ["bleu"],
                "config": self._config
            }
            response = requests.post(url=self._score_end_point, json=json.dumps(data))
            rjson = response.json()
            scores = rjson["scores"]
            assert len(scores["bleu"]) == inputs_len
            final_score_dic["bleu"] = scores["bleu"]
            final_score_dic["corpus_bleu"] = scores["corpus_bleu"]

        if "chrf" in metrics:
            data = {
                "inputs": inputs,
                "metrics": ["chrf"],
                "config": self._config
            }
            response = requests.post(url=self._score_end_point, json=json.dumps(data))
            rjson = response.json()
            scores = rjson["scores"]
            assert len(scores["chrf"]) == inputs_len
            final_score_dic["chrf"] = scores["chrf"]
            final_score_dic["corpus_chrf"] = scores["corpus_chrf"]

        # Deal with the inputs 100 samples at a time
        score_dic = defaultdict(list)
        for i in trange(0, len(inputs), BATCH_SIZE, desc="Calculating scores."):
            data = {
                "inputs": inputs[i: i + BATCH_SIZE],
                "metrics": metrics,
                "config": self._config
            }

            response = requests.post(url=self._score_end_point, json=json.dumps(data))
            rjson = response.json()
            scores = rjson["scores"]

            for k, v in scores.items():
                if "corpus" in k:
                    continue
                score_dic[k] += v

        # Aggregate scores and get corpus-level scores for some metrics
        for k, v in score_dic.items():
            assert len(v) == inputs_len
            final_score_dic[k] = v
            final_score_dic[f"corpus_{k}"] = sum(v) / len(v)

        return final_score_dic

    def signature(self):
        pass
