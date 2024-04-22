class Obfuscator:
    __mask = "*"

    def __init__(self, target):
        self.target = target

    def obfuscate(self):
        return self.__mask * len(self.target)

    def obfuscate_email(self):
        """
        Obfuscate email address
        by masking all characters except the first character before '@' and after '@'
        e.g "john.doe@dot.com" -> "j******e@d*****m"
        """
        at_index = self.target.index("@")
        visible_indices = {
            0,
            at_index - 1,
            at_index,
            at_index + 1,
            len(self.target) - 1,
        }
        return "".join(
            [
                c if idx in visible_indices else self.__mask
                for idx, c in enumerate(self.target)
            ]
        )
