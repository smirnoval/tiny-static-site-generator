import os
import sys

import utils


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
        with utils.open_file(filepath, "w", create_dir=True) as wfile:
            wfile.write(text)
