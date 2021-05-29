from PIL import Image
import hcaptcha
import imagehash
import os
import glob

class Solver:
    max_retries = 3
    min_answers = 3

    def __init__(self, data_dir=None):
        data_dir = data_dir if data_dir is not None else "./solver-data"

        self.data_dir = data_dir
        self._confirmed = {}

        self._setup_data_dir()
        self._load_data()

    @staticmethod
    def hash_image(im):
        return str(imagehash.phash(im, 8))

    @staticmethod
    def hash_question(question):
        return question.split(" ")[-1].lower().strip(".,!?")

    def get_token(self, sitekey, host, _retry=0, **kwargs):
        if _retry > self.max_retries:
            return
        
        ch = hcaptcha.Challenge(sitekey, host, **kwargs)
        q_hash = self.hash_question(ch.question)
        key_to_id = {}
        id_to_im = {}
        answers = []
        unused = []

        for key, im in ch.tasks(with_image=True):
            im_id = (q_hash, self.hash_image(im))
            key_to_id[key] = im_id
            id_to_im[im_id] = im
            if im_id in self._confirmed:
                answers.append(key)
            else:
                unused.append(key)
        
        while self.min_answers > len(answers):
            answers.append(unused.pop())
        
        token = ch.solve(answers)
        if token:
            for key in answers:
                im_id = key_to_id[key]
                if not im_id in self._confirmed:
                    self._confirm(im_id, id_to_im[im_id])
            return token
        
        return self.get_token(sitekey, host, _retry+1, **kwargs)

    def _confirm(self, im_id, im):
        if im_id in self._confirmed:
            return
        self._confirmed[im_id] = True
        im_filepath = os.path.join(self.data_dir, "confirmed", "_".join(im_id) + ".png")
        if not os.path.isfile(im_filepath):
            im.save(im_filepath)

    def _setup_data_dir(self):
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

        for subdir in ["confirmed"]:
            if not os.path.isdir(os.path.join(self.data_dir, subdir)):
                os.mkdir(os.path.join(self.data_dir, subdir))
    
    def _load_data(self):
        for sample_filepath in glob.glob(self.data_dir + "/confirmed/*.png"):
            try:
                sample = Image.open(sample_filepath)
                q_hash = os.path.basename(sample_filepath).split("_")[0]
                self._confirm((q_hash, self.hash_image(sample)), sample)
            except:
                pass
