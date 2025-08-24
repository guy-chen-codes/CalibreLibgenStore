#!/usr/bin/env python3
import sys
from lxml import etree
from urllib.request import urlopen
from urllib.parse import urlencode

def xpath(node, path):
    tree = node.getroottree()
    base_xpath = tree.getpath(node)

    return tree.xpath(base_xpath + path)

class LibgenMirror:
    def __init__(self, url, format, size, unit):
        self.url = url
        self.format = format
        self.size = size
        self.unit = unit

    @staticmethod
    def parse(node, file_type, file_size, file_size_unit):
        url = node.get('href')

        return LibgenMirror(url, file_type, file_size, file_size_unit)

class LibgenBook:
    def __init__(self, title, authors, series, md5, mirrors, language,
                 image_url):
        self.title = title
        self.authors = authors
        self.series = series
        self.md5 = md5
        self.mirrors = mirrors
        self.language = language
        self.image_url = image_url

    @staticmethod
    def parse(node):
        # Updated XPath selectors for the new libgen.li structure
        AUTHOR_XPATH = '/td[1]/a'
        SERIES_XPATH = '/td[2]'
        TITLE_XPATH = '/td[3]/a'
        LANGUAGE_XPATH = '/td[4]'
        FILE_XPATH = '/td[5]'
        MIRRORS_XPATH = '/td[6]/a'

        try:
            # Parse the Author(s) column into `authors`
            author_elements = xpath(node, AUTHOR_XPATH)
            authors = ' & '.join(filter(None, [
                author.text.strip() for author in author_elements if author.text
            ]))

            if len(authors) == 0:
                authors = 'Unknown'

            # Parse File column for file information
            file_elements = xpath(node, FILE_XPATH)
            if file_elements and file_elements[0].text:
                file_info = file_elements[0].text.strip()
                if ' / ' in file_info:
                    file_type, file_size = file_info.split(' / ', 1)
                    if '\xa0' in file_size:
                        file_size, file_size_unit = file_size.split('\xa0', 1)
                    else:
                        file_size_unit = 'KB'  # Default unit
                else:
                    file_type = file_info
                    file_size = '0'
                    file_size_unit = 'KB'
            else:
                file_type = 'Unknown'
                file_size = '0'
                file_size_unit = 'KB'

            # Parse mirrors (download links)
            mirror_elements = xpath(node, MIRRORS_XPATH)
            mirrors = []
            for mirror_elem in mirror_elements:
                if mirror_elem.get('href'):
                    mirrors.append(LibgenMirror.parse(mirror_elem, file_type, file_size, file_size_unit))

            # Parse other columns
            series_elements = xpath(node, SERIES_XPATH)
            series = series_elements[0].text.strip() if series_elements and series_elements[0].text else ''
            
            title_elements = xpath(node, TITLE_XPATH)
            if not title_elements:
                return None
                
            title = title_elements[0].text.strip() if title_elements[0].text else ''
            
            # Extract MD5 from the title link href
            title_href = title_elements[0].get('href', '')
            md5 = title_href.split('/')[-1] if title_href else ''
            
            language_elements = xpath(node, LANGUAGE_XPATH)
            language = language_elements[0].text.strip() if language_elements and language_elements[0].text else 'Unknown'

            if not authors or not title:
                return None

            return LibgenBook(title, authors, series, md5, mirrors, language, None)
            
        except Exception as e:
            print(f"Error parsing book entry: {e}")
            return None


class LibgenSearchResults:
    def __init__(self, results, total):
        self.results = results
        self.total = total

    @staticmethod
    def parse(node):
        # Updated selector for the new table structure
        SEARCH_ROW_SELECTOR = "//table[@class='c']/tbody/tr"
        
        # Fallback selector if the above doesn't work
        FALLBACK_SELECTOR = "//table/tbody/tr"

        result_rows = xpath(node, SEARCH_ROW_SELECTOR)
        
        # If no results with the primary selector, try fallback
        if not result_rows:
            result_rows = xpath(node, FALLBACK_SELECTOR)

        results = []

        for row in result_rows:
            try:
                book = LibgenBook.parse(row)
                if book is None:
                    continue

                results.append(book)
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        total = len(results)

        return LibgenSearchResults(results, total)


class LibgenClient:
    def __init__(self, mirror=None):

        MIRRORS = [
            "libgen.li",
        ]

        if mirror is None:
            self.base_url = "https://{}/".format(MIRRORS[0])
        else:
            self.base_url = "https://{}/".format(mirror)

    def search(self, query, criteria='', language='English', file_format=''):
        url = self.base_url + "index.php"
        
        # Map criteria to the new column format
        columns_map = {
            'title': 't',
            'authors': 'a', 
            'series': 's',
            'year': 'y',
            'publisher': 'p',
            'isbn': 'i'
        }
        
        # Default columns to search in
        columns = ['t', 'a', 's', 'y', 'p', 'i']
        
        # If specific criteria is provided, focus on that column
        if criteria and criteria in columns_map:
            columns = [columns_map[criteria]]
        
        # Build query parameters according to new format
        query_params = {
            'req': query,
            'res': 100,
            'filesuns': 'all'
        }
        
        # Add column parameters
        for col in columns:
            query_params[f'columns[]'] = col
            
        # Add object types (books, ebooks, etc.)
        objects = ['f', 'e', 's', 'a', 'p', 'w']
        for obj in objects:
            query_params[f'objects[]'] = obj
            
        # Add topics (literature, comics, academic, etc.)
        topics = ['l', 'c', 'f', 'a', 'm', 'r', 's']
        for topic in topics:
            query_params[f'topics[]'] = topic

        query_string = urlencode(query_params, doseq=True)
        request = urlopen(url + '?' + query_string)
        html = request.read()

        parser = etree.HTMLParser()
        tree = etree.fromstring(html, parser)

        return LibgenSearchResults.parse(tree)

    def get_detail_url(self, md5):
        detail_url = '{}{}'.format(self.base_url, md5)

        return detail_url

    def get_download_url(self, md5):
        # First, get the detail page to extract the key
        detail_url = self.get_detail_url(md5)
        
        try:
            request = urlopen(detail_url)
            html = request.read()

            parser = etree.HTMLParser()
            tree = etree.fromstring(html, parser)

            # Look for download links that contain the md5
            download_links = tree.xpath("//a[contains(@href, 'get.php') and contains(@href, '" + md5 + "')]")
            
            if download_links:
                # Extract the full download URL
                download_url = download_links[0].get('href')
                if download_url.startswith('/'):
                    download_url = self.base_url.rstrip('/') + download_url
                elif not download_url.startswith('http'):
                    download_url = self.base_url + download_url
                return download_url
            
            # Alternative: look for any link containing 'get.php'
            alt_links = tree.xpath("//a[contains(@href, 'get.php')]")
            if alt_links:
                download_url = alt_links[0].get('href')
                if download_url.startswith('/'):
                    download_url = self.base_url.rstrip('/') + download_url
                elif not download_url.startswith('http'):
                    download_url = self.base_url + download_url
                return download_url
                
        except Exception as e:
            print(f"Error getting download URL: {e}")
            
        # Fallback: construct the download URL (this may not work without the key)
        return f"{self.base_url}get.php?md5={md5}"

def main(argv):
    import argparse

    client = LibgenClient()

    parser = argparse.ArgumentParser(description="Use Libgen from the command line")
    parser.add_argument('--query', '-q', help="Search query")
    parser.add_argument('--title', '-t', help="Title to search for")
    parser.add_argument('--author', '-a', help="Author to search for")
    parser.add_argument('--series', '-s', help="Series")
    parser.add_argument('--language', '-l', help="Language")
    parser.add_argument('--format', '-f', help="Ebook format (epub, mobi, azw, azw3, fb2, pdf, rtf, txt)")

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    query = ""
    criteria = ""

    if args.query:
        query = args.query
    elif args.title:
        criteria = "title"
        query = args.title
    elif args.author:
        query = args.author
        criteria = "authors"
    elif args.series:
        query = args.series
        criteria = "series"

    print(f"Searching for: '{query}' with criteria: '{criteria}'")
    if query:
        try:
            search_results = client.search(query, criteria, args.language, args.format)
            print(f"Found {search_results.total} results")
            
            for i, result in enumerate(search_results.results[:5], 1):
                print(f"\n{i}. {result.title} by {result.authors}")
                print(f"   Series: {result.series}")
                print(f"   Language: {result.language}")
                print(f"   Detail: {client.get_detail_url(result.md5)}")
                
                download_url = client.get_download_url(result.md5)
                print(f"   Download: {download_url}")
                
        except Exception as e:
            print(f"Error during search: {e}")
    else:
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
