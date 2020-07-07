# maya_socket

Create a socket connection between Maya and an IDE for easier testing during development.

- Paste contents of server.py into Maya python console

```python
from .client import cmds, utils

print(cmds.ls())
```
