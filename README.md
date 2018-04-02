# pandoc-plantuml-filter

Pandoc filter which converts PlantUML code blocks to PlantUML images.

````
```plantuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response

Alice -> Bob: Another authentication Request
Alice <-- Bob: another authentication Response
```
````

## Usage

Install it with pip:

```
pip install pandoc-plantuml-filter
```

And use it like any other pandoc filter:

```
pandoc tests/sample.md -o sample.pdf --filter pandoc-plantuml
```

The PlantUML binary must be in your `$PATH` or can be set with the
`PLANTUML_BIN` environment variable.

## But there is ...

There are a few other filters trying to convert PlantUML code blocks however
they all failed for me.
