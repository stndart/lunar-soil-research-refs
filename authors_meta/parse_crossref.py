import dt
import requests

# Function to search for DOI using CrossRef API
def get_doi(title: str, year: int, authors: list[str]) -> list[dict]:
    url = "https://api.crossref.org/works"

    # Combine authors' last names into the query
    authors_query = " ".join(authors)
    query = f"{title} {authors_query}"

    params = {
        "query.bibliographic": query,
        "filter": f"from-pub-date:{year},until-pub-date:{year}",
        "rows": 1
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("message", {}).get("items", [])
        return items
    return []

def get_doi_pub(pub: dt.Publication) -> list[dict]:
    return get_doi(pub.Title, pub.Year.Year, [au.Name for au in pub.Authors])

def check_hit(crossref: list[dict], pub: dt.Publication) -> list[dict]:
    hits = []
    for pd in crossref:
        try:
            if pd['issued']['date-parts'][0][0] != pub.Year.Year:
                continue
            # if pub.Title.lower() not in pd['title'][0].lower():
            #     continue

            pub_authors = set([au.Name.lower() for au in pub.Authors])
            crossref_authors = set()
            for au in pd['author']:
                crossref_authors.add(au['family'].lower())
            if len(crossref_authors ^ pub_authors) > 0:
                continue
        except KeyError:
            continue
        hits.append(pd)
    return hits

def update_authors_storage(storage: dt.AllAuthors, pub: dt.Publication):
    cr_pubs = check_hit(get_doi_pub(pub), pub)
    if len(cr_pubs) == 0:
        return False
    
    for p in cr_pubs:
        for au in p.get('author', []):
            affs = []
            for aff in au.get('affiliation', []):
                affs.append(aff['name'])
            storage.add(dt.Author(Name=au['family'], Initials=au.get('given', ''), Affiliations=affs))
    return True

def ref_to_authors(ref: dict) -> list[dt.Author]:
    authors = []
    for auref in ref:
        affs = []
        for aff in auref.get('affiliation', []):
            affs.append(aff['name'])
        authors.append(dt.Author(auref['family'], auref['given'], affs))
    return authors

def ref_to_pub(ref: dict) -> dt.Publication:
    return dt.Publication(
        Title=ref['title'][0],
        Year=ref['published-print']['date-parts'][0][0],
        Authors=ref_to_authors(ref['author']),
        DOI=ref['DOI'],
        extra=ref
    )

if __name__ == '__main__':
    pub = dt.Publication(Title='Gas analysis of the lunar surface', Year=dt.PubYear(Year=1970, Letter=''),
                         Authors=[
                             dt.Author('Funkhauser', 'J.G.'),
                             dt.Author('Schaeffer', 'O.A.'),
                             dt.Author('Bogard', 'D.D.'),
                             dt.Author('Zahringer', 'J.')
                         ])
    s = dt.AllAuthors()
    update_authors_storage(s, pub)