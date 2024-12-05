from dataclasses import dataclass, field, InitVar
import re
from functools import partial
from typing import Callable

@dataclass
class Author:
    Name: str
    Initials: str
    Affiliations: list[str] = field(default_factory=list)

    def __hash__(self):
        return (self.Name + self.Initials).__hash__()
    
    def __eq__(self, other: 'Author'):
        return (self.Name + self.Initials) == (other.Name + other.Initials)
    
    def __repr__(self):
        return self.Name + ' ' + self.Initials
    
    def __add__(self, other: 'Author'):
        new_affs = set(self.Affiliations) | set(other.Affiliations)
        return Author(self.Name, self.Initials, Affiliations=new_affs)

class AllAuthors:
    def __init__(self):
        self.storage: set[Author] = set()
    
    def add(self, author: Author):
        if author in self.storage:
            au_old = list(self.storage & {author})
            if len(au_old) == 0:
                self.storage.add(author)
            else:
                self.storage.add(author + au_old[0])

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

@dataclass
class Publication:
    Title: str
    Year: PubYear
    journal: str = None
    Authors: list[Author] = field(default_factory=list)
    DOI: str = None
    extra: str = field(default=None, repr=False)

def parse_line_raw(reference: str) -> list[str]:
    reference = reference.replace('\n', '')
    
    # Pattern to match authors, year, title, and the rest
    pattern = r"^(.*?)(\(\d{4}[a-z]?\))\s+(.*?)(\.\s.*)$"
    match = re.match(pattern, reference)
    
    if not match:
        return None  # Return None if the pattern does not match
    
    authors = match.group(1).strip()
    year = match.group(2).strip("()")
    title = match.group(3).strip()
    rest = match.group(4).strip()
    
    return [authors, year, title, rest]

def split_authors(authors: str) -> list[Author]:
    author_list = []
    
    # Split the authors by commas and "and"
    author_entries = re.split(r'\s*(?:,\s*|\s+and\s+)\s*', authors)
    
    for entry in author_entries:
        # Split by spaces to separate names and initials
        name_parts = entry.strip().split()
        
        # The last part is likely the last name, others are initials
        name = ' '.join(name_parts[:-1])  # First and middle names
        initials = name_parts[-1]  # Last part is typically the initials
        
        author_list.append(Author(Name=name, Initials=initials))
    
    return author_list

def parse_line(line: str) -> tuple[list[Author], PubYear, str, str]:
    authors, year, title, rest = parse_line_raw(line)
    authors = split_authors(authors)
    year = PubYear(Year=int(year[:4]), Letter=year[4:])
    return (authors, year, title, rest)

def parse_publication(line: str) -> Publication:
    authors, year, title, rest = parse_line_raw(line)
    authors = split_authors(authors)
    year = PubYear(Year=int(year[:4]), Letter=year[4:])
    return Publication(Title=title, Year=year, Authors=authors, extra=rest)

def parse_multiple(lines: list[str], parse_fun: Callable[[list[str]], tuple[list]]):
    parsed: list[str] = []
    skipped: list[str] = []
    for i, ch in enumerate(lines):
        ps = parse_line_raw(ch)
        if ps is None or len(ps[0]) == 0:
            skipped.append((i, ch))
        else:
            parsed.append(parse_fun(ch))
    return parsed, skipped

parse_lines = partial(parse_multiple, parse_fun=parse_line)
parse_publications = partial(parse_multiple, parse_fun=parse_publication)