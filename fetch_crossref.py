import joblib

from asynched.fetch_crossref_concurrently import fetch_async_timeout, fetch_pub

if __name__ == '__main__':
    # файл получен из "doi search.ipynb" с помощью joblib.dump(parsed, 'publications.pkl')
    publications = joblib.load('publications.pkl')

    pubs_list = fetch_async_timeout(fetch_pub, timeout=20, pn=10)(publications)
    joblib.dump(pubs_list, 'pubs_full.pkl')