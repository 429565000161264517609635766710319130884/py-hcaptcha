import random
import string

def gen_widget_id():
    widget_id = "".join(random.choices(
        string.ascii_lowercase + string.digits,
        k=random.randint(10, 12)
    ))
    return widget_id