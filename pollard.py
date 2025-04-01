import math
from rabin import *

def pollard_p1(n, B):
    a = 2  # базовое число
    # Генерируем список простых чисел до B с помощью is_prime_fermat
    primes = [p for p in range(2, B + 1) if is_prime_fermat(p)]
    L = 1
    for p in primes:
        power = p
        while power * p <= B:
            power *= p
        L *= power
    a_to_L = modexp(a, L, n)
    g = math.gcd(a_to_L - 1, n)
    return g if 1 < g < n else None


n = 589
factor = pollard_p1(n, B=7)
print("Найденный делитель:", factor)
print("Второй делитель:", n // factor)