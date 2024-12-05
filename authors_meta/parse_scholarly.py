from scholarly import scholarly
import dt
from tqdm import tqdm

def get_affiliations(author_scholar_ref: dict) -> set[dt.Affiliation]:
    if 'publications' in author_scholar_ref['filled']:
        affs = set()
        affs.add(dt.Affiliation(author_scholar_ref['affiliation'], 2024))
        for pub in author_scholar_ref['publications']:
            pub_year = pub['pub_year'] if 'pub_year' in pub else 0
            if 'affiliation' in pub:
                aff = pub['affilition']
                affs.add(dt.Affiliation(aff, pub_year))
        return affs
    return set()

def get_refs(author: dt.Author) -> list[dict]:
    # Search for the author by name
    search_query = scholarly.search_author(author.__repr__())
    refs = []
    for au in search_query:
        refs.append(scholarly.fill(au))
    return refs

def fetch_author_data(author_name: str):
    all_affiliations = set()
    for au_ref in get_refs(author_name):
        affs = get_affiliations(au_ref)
        all_affiliations = all_affiliations.union(affs)
    return all_affiliations