import time

def test(a):
	if a < 10:
		print(a)
		a = a + 1
		test(a)
	return a

test(1)