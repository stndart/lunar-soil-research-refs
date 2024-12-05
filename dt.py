from dataclasses import dataclass
import re

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

def parse_line_raw(reference: str):
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

def parse_lines(lines: list[str]) -> tuple[list]:
    parsed = []
    skipped = []
    for i, ch in enumerate(lines):
        ps = parse_line_raw(ch)
        if ps is None or len(ps[0]) == 0:
            skipped.append((i, ch))
        else:
            parsed.append(parse_line(ch))
    return parsed, skipped