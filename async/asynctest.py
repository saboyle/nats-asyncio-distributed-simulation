"""
Example to demonstrate simple scatter / gather using asyncio + partials
Requires python 3.7
"""
import asyncio
import functools
import random

async def asim():
    pf = functools.partial(asim_bit)
    callables = [pf() for _f in range(10)]
    res = await asyncio.gather(*callables)
    return res

async def asim_bit():
    return random.random()

if __name__ == "__main__":
    res = asyncio.run(asim())
    print("Hello - ", res)