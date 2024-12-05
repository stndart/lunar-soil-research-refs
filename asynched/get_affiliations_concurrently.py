from scholarly import scholarly
from tqdm import tqdm
from dataclasses import dataclass
import multiprocessing as mp
import joblib
from typing import Callable

from dt import *
from authors_meta.parse_scholarly import fetch_author_data

def fetch_author_data_with_timeout(author_name: str):
    try:
        return fetch_author_data(author_name)
    except Exception as e:
        print(f"Error while fetching data for {author_name}: {e}")
        return None

def fetch_async_full(fetch: Callable[[str], set[Affiliation]], pn=10):
    def fetch_async(authors: list[Author]):
        all_authors = [au.__repr__() for au in authors]
        with mp.Pool(processes=pn) as pool:
            aff_list = list(tqdm(pool.imap_unordered(fetch, all_authors), total=len(all_authors)))
        return aff_list
    return fetch_async

def fetch_async_timeout(fetch: Callable[[str], set[Affiliation]], timeout=20, pn=10):
    def fetch_with_timeout(author_name: str):
        try:
            return fetch(author_name)
        except Exception as e:
            print(f"Error while fetching data for {author_name}: {e}")
            return None

    def fetch_async(authors: list[Author]):
        all_authors = [au.__repr__() for au in authors]
        with mp.Pool(processes=pn) as pool:
            results = []
            processes = [pool.apply_async(fetch_author_data_with_timeout, (author_name,)) for author_name in all_authors]
            for async_result in tqdm(processes):
                try:
                    results.append(async_result.get(timeout=timeout))
                except TimeoutError as e:
                    print(f"Timeout exceeded, skipping.")
                    results.append(None)
        return results

    return fetch_async


TIME_LIMIT = 20
if __name__ == '__main__':
    # файл получен из tut.ipynb с помощью joblib.dump(all_authors, 'authors.pkl')
    all_authors = list(joblib.load('authors.pkl'))[:10]

    # Оптимальный параллелизм, но если один результат парситься будет 10 минут, так и будет.
    # all_authors = [au.__repr__() for au in all_authors][:10]
    # with mp.Pool(processes=10) as pool:
    #     affiliations_list = list(tqdm(pool.imap_unordered(fetch_author_data, all_authors), total=len(all_authors)))
    
    # affiliations_list = fetch_async_full(fetch_author_data)(all_authors)


    # Неоптимальный параллелизм, но скипает результаты, которые парсятся больше TIME_LIMIT секунд.
    # all_authors = [au.__repr__() for au in all_authors][:10]
    # with mp.Pool(processes=10) as pool:
    #     results = []
    #     processes = [pool.apply_async(fetch_author_data_with_timeout, (author_name,)) for author_name in all_authors]
    #     for async_result in tqdm(processes):
    #         try:
    #             results.append(async_result.get(timeout=TIME_LIMIT))
    #         except Exception as e:
    #             print(f"Timeout exceeded, skipping.")
    #             results.append(None)

    affiliations_list = fetch_async_timeout(fetch_author_data)(all_authors)


    all_affiliations = set()
    for affiliations in affiliations_list:
        if affiliations is not None:
            all_affiliations = all_affiliations.union(affiliations)
    joblib.dump(all_affiliations, 'affiliations.pkl')
