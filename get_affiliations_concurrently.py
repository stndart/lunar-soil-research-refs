from scholarly import scholarly
from tqdm import tqdm
from dataclasses import dataclass
import multiprocessing as mp
import joblib

@dataclass
class Author:
    Name: str
    Initials: str

    def __hash__(self):
        return (self.Name + self.Initials).__hash__()

    def __repr__(self):
        return self.Name + ' ' + self.Initials

@dataclass
class PubYear:
    Year: int
    Letter: str

@dataclass
class Affiliation:
    Uni: str
    Year: int

    def __hash__(self):
        return f'{self.Uni} ({self.Year})'.__hash__()

    def __le__(self, other: 'Affiliation'):
        if self.Year < other.Year:
            return True
        if self.Year > other.Year:
            return False
        return self.Uni < other.Uni

def get_affiliations(author_scholar_ref: dict) -> set[Affiliation]:
        if 'publications' in author_scholar_ref['filled']:
            affs = set()
            affs.add(Affiliation(author_scholar_ref['affiliation'], 2024))
            for pub in author_scholar_ref['publications']:
                pub_year = pub['pub_year'] if 'pub_year' in pub else 0
                if 'affiliation' in pub:
                    aff = pub['affilition']
                    affs.add(Affiliation(aff, pub_year))
            return affs
        return set()

def fetch_author_data(author_name):
    search_query = scholarly.search_author(author_name)
    all_affiliations = set()
    for au_ref in search_query:
        au_data = scholarly.fill(au_ref)
        affs = get_affiliations(au_data)
        all_affiliations = all_affiliations.union(affs)
    return all_affiliations

def fetch_author_data_with_timeout(author_name):
    try:
        return fetch_author_data(author_name)
    except Exception as e:
        print(f"Error while fetching data for {author_name}: {e}")
        return None

TIME_LIMIT = 20


if __name__ == '__main__':
    # файл получен из tut.ipynb с помощью joblib.dump(all_authors, 'authors.pkl')
    all_authors = joblib.load('authors.pkl')
    all_authors = [au.__repr__() for au in all_authors]

    # Оптимальный параллелизм, но если один результат парситься будет 10 минут, так и будет.
    with mp.Pool(processes=10) as pool:
        affiliations_list = list(tqdm(pool.imap_unordered(fetch_author_data, all_authors), total=len(all_authors)))

    # Неоптимальный параллелизм, но скипает результаты, которые парсятся больше TIME_LIMIT секунд.
    # with mp.Pool(processes=10) as pool:
    #     results = []
    #     processes = [pool.apply_async(fetch_author_data_with_timeout, (author_name,)) for author_name in all_authors]
    #     for async_result in tqdm(processes):
    #         try:
    #             results.append(async_result.get(timeout=TIME_LIMIT))
    #         except Exception as e:
    #             print(f"Timeout exceeded, skipping.")
    #             results.append(None)

    all_affiliations = set()
    for affiliations in affiliations_list:
        if affiliations is not None:
            all_affiliations = all_affiliations.union(affiliations)
    joblib.dump(all_affiliations, 'affiliations.pkl')
