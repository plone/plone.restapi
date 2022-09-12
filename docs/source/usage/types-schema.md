---
myst:
  html_meta:
    "description": "A detailed list of all available Zope Schema field types and their corresponding representation as JSON objects."
    "property=og:description": "A detailed list of all available Zope Schema field types and their corresponding representation as JSON objects."
    "property=og:title": "Types Schema"
    "keywords": "Plone, plone.restapi, REST, API, Types, Schema"
---

(types-schema)=

# Types Schema

The following is a detailed list of all available [Zope Schema](https://zopeschema.readthedocs.io/en/latest/) field types and their corresponding representation as JSON objects.


## TextLine

Zope Schema:

```python
zope.schema.TextLine(
    title="My field",
    description="My great field",
    default="foobar"
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "default": "foobar"
}
```


## Text

Zope Schema:

```python
zope.schema.Text(
    title="My field",
    description="My great field",
    default="Lorem ipsum dolor sit amet",
    min_length=10,
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "textarea",
  "default": "Lorem ipsum dolor sit amet",
  "minLength": 10
}
```


## Bool

Zope Schema:

```python
zope.schema.Bool(
    title="My field",
    description="My great field",
    default=False,
)
```

JSON:

```json
{
  "type": "boolean",
  "title": "My field",
  "description": "My great field",
  "default": false
}
```


## Float

Zope Schema:

```python
zope.schema.Float(
    title="My field",
    description="My great field",
    min=0.0,
    max=1.0,
    default=0.5,
)
```

JSON:

```json
{
  "minimum": 0.0,
  "maximum": 1.0,
  "type": "number",
  "title": "My field",
  "description": "My great field",
  "default": 0.5
}
```


## Decimal

Zope Schema:

```python
zope.schema.Decimal(
    title="My field",
    description="My great field",
    min=Decimal(0),
    max=Decimal(1),
    default=Decimal(0.5),
)
```

JSON:

```json
{
  "minimum": 0.0,
  "maximum": 1.0,
  "type": "number",
  "title": "My field",
  "description": "My great field",
  "default": 0.5
},
```


## Int

Zope Schema:

```python
zope.schema.Int(
    title="My field",
    description="My great field",
    min=0,
    max=100,
    default=50,
)
```

JSON:

```json
{
  "minimum": 0,
  "maximum": 100,
  "type": "integer",
  "title": "My field",
  "description": "My great field",
  "default": 50
}
```


## Choice

Zope Schema:

```python
zope.schema.Choice(
    title="My field",
    description="My great field",
    vocabulary=self.dummy_vocabulary,
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "enum": ["foo", "bar"],
  "enumNames": ["Foo", "Bar"],
  "choices": [
    {"foo": "Foo"},
    {"bar": "Bar"}
  ]
}
```


## List

Zope Schema:

```python
zope.schema.List(
    title="My field",
    description="My great field",
    min_length=1,
    value_type=schema.TextLine(
        title="Text",
        description="Text field",
        default="Default text"
    ),
    default=["foobar"],
)
```

JSON:

```json
{
  "type": "array",
  "title": "My field",
  "description": "My great field",
  "default": ["foobar"],
  "minItems": 1,
  "uniqueItems": false,
  "additionalItems": true,
  "items": {
    "type": "string",
    "title": "Text",
    "description": "Text field",
    "default": "Default text"
  }
},
```


## Tuple

Zope Schema:

```python
field = zope.schema.Tuple(
    title="My field",
    value_type=schema.Int(),
    default=(1, 2),
)
```

JSON:

```json
{
  "type": "array",
  "title": "My field",
  "description": "",
  "uniqueItems": true,
  "additionalItems": true,
  "items": {
    "title": "",
    "description": "",
    "type": "integer"
  },
"default": [1, 2]
}
```


## Set

Zope Schema:

```python
field = zope.schema.Set(
    title="My field",
    value_type=schema.TextLine(),
)
```

JSON:

```json
{
  "type": "array",
  "title": "My field",
  "description": "",
  "uniqueItems": true,
  "additionalItems": true,
  "items": {
    "title": "",
    "description": "",
    "type": "string"
  }
}
```


## List of Choices

Zope Schema:

```python
field = zope.schema.List(
    title="My field",
    value_type=schema.Choice(
        vocabulary=self.dummy_vocabulary,
    ),
)
```

JSON:

```json
{
  "type": "array",
  "title": "My field",
  "description": "",
  "uniqueItems": true,
  "additionalItems": true,
  "items": {
    "title": "",
    "description": "",
    "type": "string",
    "enum": ["foo", "bar"],
    "enumNames": ["Foo", "Bar"],
    "choices": [
      {"foo": "Foo"},
      {"bar": "Bar"}
    ]
  }
}
```


## Object

Zope Schema:

```python
zope.schema.Object(
    title="My field",
    description="My great field",
    schema=IDummySchema,
)
```

JSON:

```json
{
  "type": "object",
  "title": "My field",
  "description": "My great field",
  "properties": {
    "field1": {
      "title": "Foo",
      "description": "",
      "type": "boolean"
    },
    "field2": {
      "title": "Bar",
      "description": "",
      "type": "string"
    }
  }
}
```


## RichText (`plone.app.textfield`)

Zope Schema:

```python
from plone.app.textfield import RichText
field = RichText(
    title="My field",
    description="My great field",
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "richtext"
}
```


## Date

Zope Schema:

```python
zope.schema.Date(
    title="My field",
    description="My great field",
    default=date(2016, 1, 1),
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "default": "2016-01-01",
  "widget": "date"
}
```


## DateTime

Zope Schema:

```python
zope.schema.Datetime(
    title="My field",
    description="My great field",
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "datetime"
}
```


## Email

Zope Schema:

```python
plone.schema.Email(
    title="My field",
    description="My great field",
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "email"
}
```


## Password

Zope Schema:

```python
zope.schema.Password(
    title="My field",
    description="My great field",
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "password"
}
```


## URI

Zope Schema:

```python
zope.schema.URI(
    title="My field",
    description="My great field",
)
```

JSON:

```json
{
  "type": "string",
  "title": "My field",
  "description": "My great field",
  "widget": "url"
}
```
