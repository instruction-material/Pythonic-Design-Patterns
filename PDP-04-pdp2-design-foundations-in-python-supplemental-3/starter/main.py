class Formatter:
	def format(self, text: str) -> str:
		raise NotImplementedError


class TitleFormatter(Formatter):
	def format(self, text: str) -> str:
		# TODO: return a transformed string.
		return text


def main() -> None:
	print(TitleFormatter().format("design patterns"))


if __name__ == "__main__":
	main()
