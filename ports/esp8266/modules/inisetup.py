import os
from flashbdev import bdev


def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time
    import micropython

    # Allow this loop to be stopped via Ctrl-C.
    micropython.kbd_intr(3)

    while 1:
        print(
            """\
The filesystem starting at sector %d with size %d sectors looks corrupt.
You may want to make a flash snapshot and try to recover it. Otherwise,
format it with os.VfsLfs2.mkfs(bdev), or completely erase the flash and
reprogram MicroPython.
"""
            % (bdev.start_sec, bdev.blocks)
        )
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    os.VfsLfs2.mkfs(bdev)
    vfs = os.VfsLfs2(bdev)
    os.mount(vfs, "/")
    with open("main.py", "w") as f:
        f.write(
            """\
import uasyncio as asyncio
import fildz_cyberos as cyberos

async def main():
    await cyberos.init()
    await cyberos.run_forever()
    
asyncio.run(main())
"""
        )
    return vfs
