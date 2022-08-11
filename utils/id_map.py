"""
Copy from *Stanford CS276: Information Retrieval and Web Search* Programming assignment #1
 - URL: https://web.stanford.edu/class/cs276/
"""


class IdMap:
    """
    Helper class to store a mapping from strings to ids
    """

    def __init__(self):
        self.str_to_id = {}
        self.id_to_str = []

    def __len__(self):
        """Return number of terms stored in the IdMap"""
        return len(self.id_to_str)

    def _get_str(self, i):
        """Returns the string corresponding to a given id (`i`)."""
        return self.id_to_str[i]

    def _get_id(self, s):
        """Returns the id corresponding to a string (`s`).
        If `s` is not in the IdMap yet, then assigns a new id and returns the new id.
        """
        if s not in self.str_to_id.keys():
            self.str_to_id[s] = len(self.id_to_str)
            self.id_to_str.append(s)
        return self.str_to_id[s]

    def __getitem__(self, key):
        """If `key` is a integer, use _get_str;
           If `key` is a string, use _get_id;"""
        if isinstance(key, int):
            return self._get_str(key)
        elif isinstance(key, str):
            return self._get_id(key)
        else:
            raise TypeError
