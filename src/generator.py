import os
import sys
import time
import threading

from template_engine.base import Collector
from distutils.dir_util import copy_tree
from watchcat import Watchcat

NEW_INDEX_STR = """<!DOCTYPE html>
<html>
{# templates/header.html #}
<body>
  <h1>Welcome!</h1>
  {# templates/nav.html #}
</body>
{# templates/footer.html #}
</html>"""

NEW_ABOUT_STR = """<!DOCTYPE html>
<html>
{# templates/header.html #}
<body>
  <h1>About!</h1>
  {# templates/nav.html #}
</body>
{# templates/footer.html #}
</html>"""

NEW_HEADER_STR = """
<head>
  <title>My new site</title>
  <link rel="stylesheet" href="/css/style.css" />
</head>"""

NEW_FOOTER_STR = """
<footer>
   <p><strong>Just example of footer</strong></p>
   <p>&copy; Your name </p>
</footer>"""

NEW_NAV_STR = """
  <ul>
    <li>
      <a href="/" class="active">Main</a>
    </li>
    <li>
      <a href="/about.html" class="active">About</a>
    </li>
  </ul>"""

NEW_STYLE_STR = """.active {font-weight:bold;}"""

NEW_SITE = {
    'index.html': NEW_INDEX_STR,
    'about.html': NEW_ABOUT_STR,
    'templates/header.html': NEW_HEADER_STR,
    'templates/footer.html': NEW_FOOTER_STR,
    'templates/nav.html': NEW_NAV_STR,
    'css/style.css': NEW_STYLE_STR
}


def new_site(root='.', force=False):
    if os.path.exists(os.path.join(root, 'index.html')):
        if not force:
            print("There are already index.html in the source folder.")
            sys.exit(1)

    print("Creating new site in '{0}'".format(os.path.abspath(root)))

    for filename, text in list(NEW_SITE.items()):
        filepath = os.path.join(root, filename)
        with open_file(filepath, "w", create_dir=True) as wfile:
            wfile.write(text)


def open_file(path, mode='rb', create_dir=False, create_mode=0o755):
    try:
        newfile = open(path, mode)
    except IOError:
        if not create_dir:
            raise
        newfile = None

    if not newfile:
        filedir = os.path.split(path)[0]
        os.makedirs(filedir, create_mode)
        newfile = open(path, mode)

    return newfile


def build_files(root='.', dest='site', force=False, watch=False):
    if os.path.exists(os.path.join(root, 'index.html')):
        if os.path.exists(os.path.join(root, 'site')) and not force:
            print("There are already exists folder. Try -F for rewrite.")
            sys.exit(1)
        elif not os.path.exists(os.path.join(root, 'site')):
            os.mkdir(dest)
        files_for_building = [x for x in os.listdir(root) if x[-5:] == '.html']
        for filename in files_for_building:
            build_file(filename, dest)
        stylesheet_dir = root+'/css'
        copy_tree(stylesheet_dir, root+'/'+dest+'/css')
    else:
        print("Sorry, index.html not found! Try to create new site, use for it 'new'")
        sys.exit(1)

    if watch:
        watching(root, dest)


def build_file(filename, destination, root='.'):
    res = Collector(os.path.abspath(root), "/" + filename).assemble_page(destionation_url=str(destination))
    with open(os.path.abspath(root) + "/" + destination + "/" + filename, 'w') as f:
        f.write(res)


def watching(root='./', dest='site'):
    """There you can connect any watcher whatever you like.
       For that you need..."""
    dirs_for_watching = [root, root+'/templates/', root+'/css/']
    files_for_watching = []
    for adress in dirs_for_watching:
        files_in_dir = os.listdir(os.path.realpath(adress))
        files_for_watching += [os.path.realpath(adress+x) for x in files_in_dir if os.path.isfile(adress+x) and (x[-5:]=='.html' or x[-4:]=='.css')]
    watchcat = Watchcat(*files_for_watching)
    watching_thread = threading.Thread(target=watchcat.run_watching())
    watching_thread.start()
    try:
        num_changes = 0
        while True:
            time.sleep(0.5)
            if num_changes < watchcat.num_changes:
                build_files(root=root, dest=dest, force=True)
                num_changes = watchcat.num_changes
    except KeyboardInterrupt:
        watching_thread.join()
