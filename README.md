# quicksettings
A zero dependency package to manage python application configuration.

## Installation

`pip install quicksettings`

## Getting started

```py
from dataclasses import InitVar, dataclass

from quicksettings import BaseSettings


@dataclass(init=False)
class Settings(BaseSettings):
    env_prefix: InitVar[str] = "FOO_"

    USERNAME: str
    PASSWORD: str = "slightly-secret"


settings = Settings()
```

The snippet above will set the value of `settings.USERNAME` to the value of the `FOO_USERNAME` environment variable.
`settings.PASSWORD` will default to the supplied value if the related environment variable is not set. Thus, environment variables take precedence over defaults.

If fields with no defaults are declared without corresponding environment variables, an exception will be raised.

## Supported field types

* `str`
* `int`
* `float`
* `bool`
* `list`
* `dict`

`list` and `dict` types can even contain each other, nested.

## Known limitations

* Since we're working with vanilla dataclasses, values with defaults cannot be defined before values without defaults. If your application is running python >= 3.10, the dataclass `kw_only` arg can be supplied.
* While basic container types are supported (list & dict), nested dataclasses are not.
* No dotenv support - it's up to you to set up the environment.
* Field names are case sensitive by default
* Union field types other than `<type> | None` might bug out, not sure if there's a use case for this.
