# Alphacoders

```
pip install alphacoders
python3 -m alphacoders -h
```

The package also provides a Python interface which is recommended to use.

```python
from alphacoders import Search, DefaultFolder
from pathlib import Path

Search('C.C.') >> DefaultFolder()  # create a folder called "C.C." and save over 3000 images
Search('C.C.')[:20] >> DefaultFolder()  # save the first 20 images
Path('images').mkdir()
(Search('C.C.') | Search('C++')) >> Path('images')  # unify result
Search('C.C.', mobile=True) >> DefaultFolder()  # search on mobile site
```