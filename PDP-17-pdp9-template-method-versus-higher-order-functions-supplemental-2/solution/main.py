#################
#   CONSTANTS   #
#################

SAMPLE_TEXT = "design patterns"


#############
#   TYPES   #
#############


# Define the formatting strategy interface
class Formatter:
    """Define the formatter interface"""

    def format(self, text: str) -> str:
        """Format the provided text"""
        raise NotImplementedError


# Format text by capitalizing the first letter of each word
class TitleFormatter(Formatter):
    """Format text in title case"""

    def format(self, text: str) -> str:
        """Convert text to title case"""
        return text.title()


#################
#   FUNCTIONS   #
#################


def main() -> None:
    """Print a title-formatted sample phrase"""
    print(TitleFormatter().format(SAMPLE_TEXT))


if __name__ == "__main__":
    main()
