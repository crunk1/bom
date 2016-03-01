import bs4
import glob
import os
import requests

dirpath = '/home/scott/workspace/bom/'
url_format = 'https://lds.org/scriptures/bofm/%s/%s?lang=eng'

books = [
  ('1-ne', 22), ('2-ne', 33), ('jacob', 7), ('enos', 1), ('jarom', 1), ('omni', 1), ('w-of-m', 1), ('mosiah', 29), ('alma', 63), ('hel', 16), ('3-ne', 30), ('4-ne', 1), ('morm', 9), ('ether', 15), ('moro', 10)
]

def get_path(book_index):
  path_pattern = os.path.join(dirpath, '%s_*' % str(book_index).zfill(2))
  paths = glob.glob(path_pattern)
  assert len(paths) == 1
  return paths[0]


def generate_file(chapter_path, book, chapter):
  to_write = ''
  content = requests.get(url_format % (book[0], chapter)).text
  soup = bs4.BeautifulSoup(content, 'html.parser')
  if chapter == 1:
    to_write += str(soup.h1.span.string).upper() + '\n\n'
  to_write += 'CHAPTER %s\n' % chapter

  # Write Summary
  summary = soup.find_all('div', 'summary')[0].p
  to_write += '\n'
  for child in summary.children:
    to_write += unicode(child.string)
  to_write += '\n'

  # Write verses
  verses_element = soup.find(id='0')
  verse_elements = verses_element.find_all('p')
  for i, element in enumerate(verse_elements):
    to_write += '\n%s\n' % (i + 1)
    for child in element.children:
      if child.name in [u'span', u'sup']:
        continue
      elif child.name == u'a' and 'bookmark-anchor' in child.get('class'):
        continue
      else:
        to_write += unicode(child.string)
  with open(chapter_path, 'w') as f:
    f.write(to_write.encode('utf8'))

for i in range(len(books)):
  book = books[i]
  book_path = get_path(i)
  chapters = range(1, book[1] + 1)
  for chapter in chapters:
    chapter_path = os.path.join(book_path, str(chapter).zfill(2))
    print chapter_path
    if os.path.exists(chapter_path):
      continue
    generate_file(chapter_path, book, chapter)
