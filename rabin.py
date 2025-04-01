import random
import math


def modexp(base, exponent, modulus):
    """
    Быстрое возведение в степень по модулю.
    Вычисляет (base^exponent) mod modulus.
    """
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result


def is_prime_fermat(n, k=20):
    """
    Простейшая проверка на простоту с использованием теста Ферма.
    Для нечетных n > 2.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    for _ in range(k):
        a = random.randint(2, n - 2)
        if modexp(a, n - 1, n) != 1:
            return False
    return True


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.
    Возвращает тройку (g, x, y), где g = gcd(a, b) и x, y удовлетворяют уравнению: a*x + b*y = g.
    """
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def generate_prime_4k3(bit_length=16):
    """
    Генерирует простое число p, удовлетворяющее условию p % 4 = 3,
    с приблизительной длиной бит, равной bit_length.
    """
    while True:
        candidate = random.getrandbits(bit_length)
        candidate |= 1  # гарантируем нечетность
        # Приводим число к виду 4k+3
        if candidate % 4 != 3:
            candidate += (3 - (candidate % 4))
        if is_prime_fermat(candidate, k=10):
            return candidate


def chunk_string(s, chunk_len):
    """
    Разбивает строку s на куски по chunk_len бит.
    Если последний блок короче, дополняет его слева нулями.
    """
    chunks = []
    for i in range(0, len(s), chunk_len):
        block = s[i:i + chunk_len]
        if len(block) < chunk_len:
            block = block.zfill(chunk_len)
        chunks.append(block)
    return chunks


def rabin_encrypt_block(m, n):
    """
    Шифрует блок m по схеме Рабина: c = (m^2) mod n.
    """
    return (m * m) % n


def mod_sqrt(a, p):
    """
    Находит квадратные корни числа a по модулю простого числа p.
    Если решений нет – возвращает пустой список.
    Предполагается, что p ≡ 3 (mod 4).
    """
    a = a % p  # обязательно приводим a к остатку по модулю p
    if a == 0:
        return [0]
    # Если a не является квадратичным вычетом, решений нет.
    if modexp(a, (p - 1) // 2, p) != 1:
        return []
    x = modexp(a, (p + 1) // 4, p)
    return sorted({x, p - x})


def crt_combine(a, b, p, q):
    """
    Решает систему сравнений:
        x ≡ a (mod p)
        x ≡ b (mod q)
    с использованием Китайской теоремы об остатках.
    """
    _, y_p, y_q = extended_gcd(p, q)
    return (a * q * y_q + b * p * y_p) % (p * q)


def mod_sqrt_rabin(c, p, q):
    """
    Находит все 4 квадратных корня числа c по модулю n = p * q с использованием КТО.
    """
    roots_p = mod_sqrt(c, p)
    roots_q = mod_sqrt(c, q)
    solutions = []
    for rp in roots_p:
        for rq in roots_q:
            solutions.append(crt_combine(rp, rq, p, q))
    return sorted(solutions)





if __name__ == "__main__":
    p = generate_prime_4k3(bit_length=16)
    q = generate_prime_4k3(bit_length=16)
    p = 31
    q = 19
    n = p * q
    print("Сгенерированные ключи:")
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  n = p * q = {n}\n")
    plaintext = input("Введите текст для шифрования: ")
    print(f"\nИсходный текст: {plaintext}")

    # Преобразование текста в двоичную строку (ASCII)
    ascii_codes = [ord(ch) for ch in plaintext]
    bit_string = ''.join(f"{code:08b}" for code in ascii_codes)
    print(f"\nДвоичная строка (без дополнения):")
    print(f"  {bit_string} (длина {len(bit_string)} бит)")

    # Определяем размер блока как floor(log2(n))
    block_size = int(math.floor(math.log2(n)))

    # Дополняем строку слева нулями, чтобы её длина была кратна block_size
    remainder = len(bit_string) % block_size
    padding = (block_size - remainder) % block_size
    bit_string_padded = bit_string.zfill(len(bit_string) + padding)
    print(f"\nДвоичная строка после дополнения:")
    print(f"  {bit_string_padded} (длина {len(bit_string_padded)} бит)")

    # Разбиваем строку на блоки по block_size бит
    blocks = chunk_string(bit_string_padded, block_size)
    print(f"\nПолучено блоков: {len(blocks)}")
    print("Блоки:")
    print(f"  {blocks}")
    print([int(b, 2) for b in blocks])

    cipher_blocks = []
    for block in blocks:
        m = int(block, 2)
        c = rabin_encrypt_block(m, n)
        cipher_blocks.append(c)
    print(f"\nЗашифрованные блоки:")
    print(f"  {cipher_blocks}")

    # Демонстрация возможных вариантов расшифрования
    print("\nВозможные варианты расшифрования для каждого блока:")
    for idx, c in enumerate(cipher_blocks, start=1):
        possible_ms = mod_sqrt_rabin(c, p, q)
        print(f"  Блок {idx} (c = {c}): возможные m = {possible_ms}")
