import random


chars = 'abcdefghijklmnopqrstuvxyz01234567890_-!*'
key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
print("SECRET_KEY = '%s'" % key)
