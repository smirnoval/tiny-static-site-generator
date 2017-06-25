# tiny-static-site-generator

tiny-static-site-generator is the simpliest and tinies static site generator that your ever see.

##Requirements
List of requirements:
1) Python 3.2+
2) That's all!

## Creating new site

```
python3 args.py new
```

This command creates templates of site with such files and dirs:
-index.html
-about.html
-css/style.css
-templates/footer.html
-templates/header.html
-templates/nav.html

## Building site

```
python3 args.py build
```

This command build all source files into ready-to-deploy site into folder that you indicated(or not, default='site').

## Serving Site

```
python3 args.py serve
```

Serve site on specifield port(default='8000')

## List of commands

'build' -- Build all source files into ready-to-deploy site
'serve' -- Serve site
'new' -- Create new site's templates
'-r', '--root' -- The root folder wuth your source files, default='.'
'-o', '--output' -- The folder where your files should be placed, default='site'
'-p', '--port' -- The port to be used for the http server, default=8000
'-w', '--watch' -- Scan for changes
'-f', '--force' -- Build this site even if there already exists index.html


## Built-in projects
Tiny-static-site-generator includes built-in template engine (https://github.com/smirnoval/simple-template-engine)
and library that watches for changes (https://github.com/smirnoval/watchcat).

## Contributing

I always need help, so join.
Fork the repository on GitHub and send a pull request, or file an issue ticket at the issue tracker. 


