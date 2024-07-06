import time
def time_ns():
    # take current time
    t = time.time()
    # convert to nanoseconds
    return int(t * 1e9)



def time_float():
    nanoseconds = time_ns()
    # Convert nanoseconds to microseconds
    microseconds = nanoseconds // 1000
    # Convert microseconds to seconds (as a float)
    seconds = microseconds / 1_000_000
    return seconds

# Example usage
t1 = time.time()
t2 = time_float()
print(f'built in time(): {t1}, custom time_float(): {t2}, difference: {t1 - t2}')