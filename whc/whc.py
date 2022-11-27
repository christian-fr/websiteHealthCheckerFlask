# !/usr/bin/env python3
# asyncq.py
import datetime
import os
import time
import json
from typing import List
import requests
from requests import ReadTimeout
from whc.smtputil import smtp_send_mail
import asyncio
import datetime
import itertools as it
import os
import random
import time
from typing import List


def main(url_list: List[str], check_interval: int, **kw) -> None:
    while True:
        str_date_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        for url in url_list:
            try:
                r = requests.get(url, timeout=30)
            except ReadTimeout as e:
                print(e)
                smtp_send_mail(content=f'{url=} timeout: {e}', subject=f'ERROR: {url=} page not loaded', **kw)

            encoding = 'iso-8859-15'
            if hasattr(r, 'headers'):
                if 'Content-Type' in r.headers:
                    if 'charset=utf-8' in r.headers['Content-Type'].lower():
                        encoding = 'utf-8'

            if r.status_code == 200:
                print(f'{str_date_time} {url=} is working with status code 200.')
                # send_mail(content=f'{URL=} is working with status code 200.', subject=f'WORKING: {URL=}')
                if r.content.decode(encoding).find('Willkommen zu unserer Befragung') == -1:
                    print(
                        f'{str_date_time} {url=} \n\n is working with status code 200, but here is the page content: \n\n{r.content.decode(encoding)=}')
                    smtp_send_mail(
                        content=f'{url=} \n\nis working with status code 200, but here is the page content: \n\n{r.content.decode(encoding)=}',
                        subject=f'ERROR: {url=} page not loaded', **kw)
            elif r.status_code != 200:
                print(f'{str_date_time} {url=} sends {r.status_code=}.')
                smtp_send_mail(content=f'{url=} sends {r.status_code=}.', subject=f'ERROR: {url=} {r.status_code=}',
                               **kw)
        time.sleep(check_interval)


def ts_str() -> str:
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


async def controller(q: asyncio.Queue, task_list: dict) -> None:
    old_size = 0
    while True:
        list_to_do = [(ts, e) for ts, e in task_list.items() if ts < time.time()]
        if list_to_do:
            print(f'controller: {time.time()}')
            events_to_remove = []
            for event in list_to_do:
                events_to_remove.append(event)
                offset = event[1][0]
                subframe = event[1][1]
            for event in events_to_remove:
                task_list.pop(event[0])

        await asyncio.sleep(0.05)
        if q.qsize() > old_size:
            # print(f'queue increased size: {q.qsize()}')
            i = await q.get()
            if isinstance(i, dict):
                TASK_LIST.update(i)
        # elif q.qsize() < old_size:
        #    print(f'queue decreased size: {q.qsize()}')
        # old_size = q.qsize()


def health_checker(url: str, q: asyncio.Queue, check_interval: int, **kw):
    s = ts_str()
    try:
        r = requests.get(url, timeout=30)
        encoding = 'iso-8859-15'
        if hasattr(r, 'headers'):
            if 'Content-Type' in r.headers:
                if 'charset=utf-8' in r.headers['Content-Type'].lower():
                    encoding = 'utf-8'

        if r.status_code == 200:
            print(f'{ts_str()} {url=} is working with status code 200.')
            # send_mail(content=f'{URL=} is working with status code 200.', subject=f'WORKING: {URL=}')
            if r.content.decode(encoding).find('Willkommen zu unserer Befragung') == -1:
                print(
                    f'{ts_str()} {url=} \n\n is working with status code 200, but here is the page content: \n\n{r.content.decode(encoding)=}')
                smtp_send_mail(
                    content=f'{url=} \n\nis working with status code 200, but here is the page content: \n\n{r.content.decode(encoding)=}',
                    subject=f'ERROR: {url=} page not loaded', **kw)
        elif r.status_code != 200:
            print(f'{ts_str()} {url=} sends {r.status_code=}.')
            smtp_send_mail(content=f'{url=} sends {r.status_code=}.', subject=f'ERROR: {url=} {r.status_code=}', **kw)
    except ReadTimeout as e:
        print(e)
        smtp_send_mail(content=f'{url=} timeout: {e}', subject=f'ERROR: {url=} page not loaded', **kw)
    finally:
        timestamp = time.time()
        next_timing = timestamp + check_interval
        e = {next_timing: (url, check_interval)}
        await q.put(e)


async def produce(name: int, q: asyncio.Queue, offset: int) -> None:
    while True:
        # n = random.randint(0, 10)
        # for _ in it.repeat(None, n):  # Synchronous loop for each single producer
        next_timing = 0
        while True:
            if next_timing > time.time():
                await asyncio.sleep(0.05)
                continue
            increment = random.randint(1, 3)
            next_timing = time.time() + increment
            print(f'produced {name} setting ts + {increment}s')
            e = {next_timing: (offset, [random.randint(0, 255) for _ in range(10)])}
            await q.put(e)
            # i = await makeitem()
            # t = time.perf_counter()
            # await q.put((i, t))
            print(f"Producer {name} added <{e}> to queue.")


TASK_LIST = {}


async def consume(name: int, q: asyncio.Queue, task_list: dict) -> None:
    while True:
        # await asyncio.sleep(3)
        # i, t = await q.get()
        # now = time.perf_counter()
        # print(f"Consumer {name} got element <{i}>")
        # q.task_done()
        await asyncio.sleep(0.01)


async def main(nprod: int, ncon: int, nuniv: int):
    q = asyncio.Queue()

    producers = [asyncio.create_task(produce(n, q, n * 11)) for n in range(nprod)]
    # consumers = [asyncio.create_task(consume(n, q, TASK_LIST)) for n in range(ncon)]
    controllers = [asyncio.create_task(controller(q, TASK_LIST))]
    await asyncio.gather(*producers)
    await q.join()  # Implicitly awaits consumers, too
    for c in controllers:
        c.cancel()


if __name__ == '__main__':
    # TIME_INTERVAL = 'TIME_INTERVAL'
    # URLS_LIST = 'URLS_LIST'
    # _INTERVAL = os.environ[TIME_INTERVAL]
    # _URLS_LIST = json.loads(os.environ[URLS_LIST])

    interval = 120
    urls_list = ['https://presentation.dzhw.eu/Test_Modul']
    urls_list = ['https://www.dzhw.eu']

    mail_address = os.environ['MAIL_ADDRESS']
    mail_pass = os.environ['MAIL_PASS']
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = os.environ['SMTP_PORT']
    # smtp_auth = os.environ[SMTP_AUTH]
    # smtp_tls = os.environ[SMTP_TLS]
    mail_to = os.environ['MAIL_TO']

    main(url_list=urls_list, check_interval=interval, mail_addr=mail_address, mail_pass=mail_pass,
         smtp_server=smtp_server, smtp_port=smtp_port, mail_to=mail_to)
