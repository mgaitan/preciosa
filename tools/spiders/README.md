Preciosa Spiders
----------------

## Running a spider

To run a spider install requirements.txt by running:
`pip install -r requirements.txt`

After that you should have scrapy as a cli tool, check that by running:
`scrapy version`

cd to the same level dir where is the scrapy.cfg file and run: 
```
scrapy crawl <name-of-the-spider> -o output.csv -t csv
```

For example:
```
scrapy crawl discovirtual -o /home/data/discovirtual.csv -t csv
```


## Running tests

Install nosetests. 

Tag your integration tests with 

```python
from nose.plugins.attrib import attr


@attr('integration')
class MyTestCase:
    def test_long_integration(self):
        pass
    def test_end_to_end_something(self):
        pass
```

And run avoid integration tests with the following command
```
$ nosetests -a '!integration'
```

