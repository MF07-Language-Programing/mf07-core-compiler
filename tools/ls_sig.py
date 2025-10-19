from inspect import signature
from pygls.server import LanguageServer
print(signature(LanguageServer.__init__))
