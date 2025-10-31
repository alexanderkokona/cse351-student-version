def fib(n):
    # (10) 1 + 1 + 2 + 3 + 5 +
    previous = 0
    number =  1
    for _ in range(n - 1):
        temp = number
        number = number + previous
        previous = temp
    return number
# memoization
def rec_fib(n):
    # fib(10) = fib (9) + fib(8)
    if n <= 2:
        return 1
    return rec_fib(n - 1) + rec_fib(n - 2)


if __name__ == '__main__':
    print (fib(4))
    print (rec_fib(4))