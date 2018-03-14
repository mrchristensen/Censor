s/(#include\s*<[[:alpha:].]+>)/#pragma BEGIN \1\n\1\n#pragma END/
