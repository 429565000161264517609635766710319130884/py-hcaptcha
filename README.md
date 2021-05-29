# py-hcaptcha
Python library for interacting with hCaptcha

# Solver Usage
Training is required for the solver to function properly. Use https://github.com/h0nde/py-hcaptcha/blob/main/tools/gather_data.py.

```python
import hcaptcha

solver = hcaptcha.Solver(data_dir="./solver-data")
token = solver.get_token(
    sitekey="45fbc4de-366c-40ef-9274-9f3feca1cd6c",
    host="v3rmillion.net",
    http_client=None)

print("result:", token)
```

# Usage
```python
import hcaptcha

ch = hcaptcha.Challenge(
    sitekey="45fbc4de-366c-40ef-9274-9f3feca1cd6c",
    host="v3rmillion.net",
    http_client=None # xrequests.Session, or requests.Session
)
print(ch.question)

answers = []
for key, im in ch.tasks():
    im.show()
    if input("Press any key to add this image as an answer: "):
        answers.append(key)

token = ch.solve(answers)
print("response:", token)
```

# Installation
```bash
pip install -U git+https://github.com/h0nde/xrequests
pip install -U git+https://github.com/h0nde/py-hcaptcha
```
