import logging
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from transformers import RobertaTokenizer

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class PasswordModel(BaseModel):

    def __init__(self,
                 model='SAP/password-model-onnx',
                 tokenizer='microsoft/codebert-base-mlm'):
        """
        Parameters
        ----------
        model: str
            The model path or HuggingFace repo id (e.g. 'SAP/password-model-onnx')
        tokenizer: str
            The tokenizer path or repo id
        """
        self.tokenizer = RobertaTokenizer.from_pretrained(tokenizer)
        try:
            # Download model.onnx from HuggingFace repository if repo ID is given or file exists
            if not model.endswith('.onnx'):
                onnx_path = hf_hub_download(repo_id=model, filename="model.onnx")
            else:
                onnx_path = model
            self.session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        except Exception as e:
            logger.warning(f"Could not load ONNX model session from {model}: {e}")
            self.session = None

    def analyze_batch(self, discoveries):
        """ Analyze a snippet and predict whether it is a leak or not.
        Change each discovery state in-place.

        Parameters
        ----------
        discoveries: list of dict
            The discoveries to classify

        Returns
        -------
        discoveries: list of dict
            The discoveries, with states updated according to
            the model's predictions
        """
        if not self.session:
            return discoveries

        new_discoveries = [d for d in discoveries if d['state'] == 'new']
        no_new_discoveries = [d for d in discoveries if d['state'] != 'new']

        if new_discoveries:
            snippets = [d['snippet'] for d in new_discoveries]
            predictions = self._predict_snippets(snippets)
            for d, p in zip(new_discoveries, predictions):
                if p == 0:
                    d['state'] = 'false_positive'

        return new_discoveries + no_new_discoveries

    def analyze(self, discovery):
        """ Analyze a snippet and predict whether it is a leak or not.

        Parameters
        ----------
        discovery: dict
            The discovery dictionary

        Returns
        -------
        bool
            True if the snippet is safe (i.e., false positive / no leak).
            False otherwise
        """
        if not self.session:
            return False

        predictions = self._predict_snippets([discovery['snippet']])
        if len(predictions) > 0 and predictions[0] == 0:
            return True
        return False

    def _predict_snippets(self, snippets):
        """ Run ONNX inference on a list of snippets. """
        if not self.session or not snippets:
            return []

        encodings = self.tokenizer(snippets, truncation=True, padding=True, return_tensors="np")
        inputs = {k: np.array(v, dtype=np.int64) for k, v in encodings.items() if k in [inp.name for inp in self.session.get_inputs()]}

        outputs = self.session.run(None, inputs)
        logits = outputs[0]
        predictions = np.argmax(logits, axis=1)
        return predictions
