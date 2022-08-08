# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.



```py linenums="1" hl_lines="2 3"
{%
    include "../tests/docs/test_try.py" 
    start="# [first_block__start]"
    end="# [first_block__end]"
%}
```

```bash
>>> 10
```


=== "TEST with a long string"

    ```py linenums="1" hl_lines="2 3"
    {%
        include "../tests/docs/test_try.py" 
        start="# [second_block__start]"
        end="# [second_block__end]"
    %}
    ```

=== "C++"

    ``` c++
    #include <iostream>

    int main(void) {
      std::cout << "Hello world!" << std::endl;
      return 0;
    }
    ```