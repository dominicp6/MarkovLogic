import timeit

py = timeit.timeit('primes_py.primes(1000)', setup='import primes_py', number=100)

cy = timeit.timeit('primes.primes(1000)', setup='import primes', number=100)

print(cy, py)
print(f'Cython is {int(py/cy)}x faster')

