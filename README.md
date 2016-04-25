# utilities

An app that provides mundane utility functions to be used as a dependency of other apps.

## Functions

<a name="size_x1" />
### `size_x1(collection a)`: Gets the size of an array or map using 1 core.

*Input*: /dynamic

*Returns*: /integer

*Example*:

```
{
  "function": {
    "account": "youraccount",
    "app": "utilities",
    "name": "size_x1",
    "args": [{
      "value": [1, 2, 3]
    }]
  }
}
```

<a name="size_x2" />
### `size_x2(collection a)`: Gets the size of an array or map using 2 cores.

See [`size_x1`](#size_x1) above.

<a name="size_x4" />
### `size_x4(collection a)`: Gets the size of an array or map using 4 cores.

See [`size_x1`](#size_x1) above.

<a name="size_x8" />
### `size_x8(collection a)`: Gets the size of an array or map using 8 cores.

See [`size_x1`](#size_x1) above.

<a name="size_x16" />
### `size_x16(collection a)`: Gets the size of an array or map using 16 cores.

See [`size_x1`](#size_x1) above.