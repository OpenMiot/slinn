import sys, importlib
if 'example.app' not in sys.modules.keys():
    from tcp_example.app import dp
else:
    dp = importlib.reload(sys.modules['example.app']).dp