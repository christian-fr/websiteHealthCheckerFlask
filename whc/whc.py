import datetime
import os
import time
import json
from typing import List

import requests
from requests import ReadTimeout

from whc.smtputil import smtp_send_mail


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


if __name__ == '__main__':
    # TIME_INTERVAL = 'TIME_INTERVAL'
    # URLS_LIST = 'URLS_LIST'
    # _INTERVAL = os.environ[TIME_INTERVAL]
    #_URLS_LIST = json.loads(os.environ[URLS_LIST])

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
