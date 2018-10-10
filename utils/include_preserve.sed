s/(^\s*#include\s*("|<)([[:alnum:].\/])+("|>))/#pragma BEGIN \1\n\1\n#pragma END \1/
#s/(^\s*#include\s*<[[:alpha:].]+>)/#pragma BEGIN \1\n\1\n#pragma END/
