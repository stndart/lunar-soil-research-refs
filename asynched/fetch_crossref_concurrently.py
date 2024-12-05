from tqdm import tqdm
from dataclasses import dataclass
import multiprocessing as mp
import joblib
from typing import Callable, Any
from itertools import chain

from multiprocessing.context import TimeoutError as MPTimeoutError

import dt
from authors_meta.parse_crossref import get_doi_pub, check_hit

def fetch_pub(pub: dt.Publication) -> list[dict]:
    try:
        return check_hit(get_doi_pub(pub), pub)
    except Exception as e:
        print(f"Error while fetching data for {pub.Title}: {e}")
        return None

def fetch_async_full(fetch: Callable[[dt.Publication], Any], pn=10):
    def fetch_async(pubs: list[dt.Publication]) -> list[Any]:
        with mp.Pool(processes=pn) as pool:
            res = list(tqdm(pool.imap_unordered(fetch, pubs), total=len(pubs)))
        return chain(*res)
    return fetch_async

def fetch_with_timeout(pub: dt.Publication, fetch: Callable):
    try:
        return fetch(pub)
    except Exception as e:
        print(f"Error while fetching data for {pub.Title}: {e}")
        return None

def fetch_async_timeout(fetch: Callable[[dt.Publication], Any], timeout=20, pn=10):

    def fetch_async(pubs: list[dt.Publication]) -> list[Any]:
        with mp.Pool(processes=pn) as pool:
            results = []
            processes = [pool.apply_async(fetch_with_timeout, (pub, fetch)) for pub in pubs]
            for async_result in tqdm(processes):
                try:
                    results.append(async_result.get(timeout=timeout))
                except MPTimeoutError as e:
                    print(f"Timeout exceeded, skipping.")
                    results.append(None)
        return results

    return fetch_async