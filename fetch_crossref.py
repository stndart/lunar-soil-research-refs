import joblib

from asynched.fetch_crossref_concurrently import fetch_async_timeout, fetch_pub

if __name__ == '__main__':
    # файл получен из "doi search.ipynb" с помощью joblib.dump(parsed, 'publications.pkl')
    publications = joblib.load('publications.pkl')

    authors_list = fetch_async_timeout(fetch_pub, timeout=10, pn=30)(publications)
    joblib.dump(authors_list, 'authors_full.pkl')