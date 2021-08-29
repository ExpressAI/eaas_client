from typing import List, Dict
import requests
import json
import warnings


class Client:
    def __init__(self):
        """ A client wrapper """
        # self.end_point = "http://18.224.144.134/"
        self.end_point = "http://piaget.lti.cs.cmu.edu:6666/score"
        self.valid_metrics = [
            "bart_score_src",
            "bart_score_ref",
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
        pass

    def metrics(self):
        pass

    def score(self, inputs: List[Dict], metrics=None):
        if metrics is None:
            metrics = self.valid_metrics
        else:
            for metric in metrics:
                assert metric in self.valid_metrics, "Your have entered invalid metric, please check."
            warnings.warn("You didn't specify the metrics, will use all valid metrics by default.")

        data = {
            "inputs": inputs,
            "metrics": metrics
        }
        response = requests.post(url=self.end_point, json=json.dumps(data))
        rjson = response.json()
        print(f"output: {rjson}")
        pass

    def signature(self):
        pass