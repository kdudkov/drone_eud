# /usr/bin/env python3
import asyncio
import functools
import random
import time

class App(object):
    data = dict()
    running = False
    addr = None
    queue = asyncio.Queue(100)

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, ex):
        self.addr = None
        print(ex)

    def datagram_received(self, data, addr):
        loop = asyncio.get_running_loop()
        self.addr = addr
        self.queue.put_nowait(data)

    async def run(self):
        loop = asyncio.get_running_loop()
        self.running = True

        transport, protocol = await loop.create_datagram_endpoint(lambda: self, local_addr=('0.0.0.0', 50000))
        transport, protocol = await loop.create_datagram_endpoint(lambda: self, local_addr=('0.0.0.0', 40000))

        fut = asyncio.ensure_future(self.cron(), loop=loop)
        asyncio.ensure_future(self.reader(), loop=loop)
        #loop.call_soon(self.cron)
        #loop.run_until_complete(fut)
        await asyncio.sleep(3600)

    async def reader(self):
        while self.run:
            d = await self.queue.get()
            if d[0] != 0x68:
                print('invalid prefix - 0x%.2x'% d[0])
                print(' '.join(('%.2x' % x for x in d)))
                continue
            ch = 0
            for x in d[1:-1]:
                ch ^= x

            if ch != d[-1]:
                print('invalid checksum')
                continue

            if d[2] != len(d) - 4:
                print('invalid len')
                continue
            await self.process_message(d[1], d[3:-1])


    async def process_message(self, mt, data):
        if mt == 0x0b:
            pass
        elif mt == 0x1b:
            pass
        elif mt == 0x0a:
            self.send_message(0x8a, [0x58,0x4c,0x30,0x31,0x32,0x53,0x46,0x58,0x78,0x80,0x0c,0x08])
        elif mt == 0x7e:
            self.send_message(0xfe, b'HF-XL-XL012S011.021.1222')
        else:
            print('%.2x' % mt)
            print(' '.join(('%.2x' % x for x in data)))

    async def cron(self):
        random.seed()

        while self.running:
            self.data['roll'] = self.data.get('roll', 0.0) + float(random.randint(0, 100) - 50) / 20
            self.data['pitch'] = self.data.get('pitch', 0.0) + float(random.randint(0, 100) - 50) / 20
            self.data['yaw'] = self.data.get('yaw', 0.0) + float(random.randint(0, 100) - 50) / 20

            # gyro
            data = [0x39,0x00,0xf3,0x00,0x7e,0x3d,0xfb,0x00,0x29,0x00,0x00,0x00,0x00,0x07]
            data[0] = random.randint(0, 255)
            data[1] = random.randint(0, 255)
            self.send_message(0x8b, data)

            # coords
            data = [1,0,0,0,0,0,0,0,0,0xe8,0x03,0,0]
            self.send_message(0x8c, data)

            # battery
            data = [0xc0,0xf0,0x0c,0x00,0x00,0x01,0x00,0x00]
            self.send_message(0x8f, data)

            await asyncio.sleep(.2)

    def send_message(self, code, msg):
        if self.addr is not None:
            d = [0x58]
            d.append(code)
            d.append(len(msg))
            for dd in msg:
                d.append(dd)
            ch = 0
            for x in d[1:]:
                ch ^= x
            d.append(ch)
            self.transport.sendto(bytes(d), self.addr)

    def do_async(self, fn, *args):
        if asyncio.iscoroutinefunction(fn):
            asyncio.ensure_future(fn(*args), loop=self.loop)
        else:
            self.loop.call_soon(functools.partial(fn, *args))

if __name__ == '__main__':
    asyncio.run(App().run())
