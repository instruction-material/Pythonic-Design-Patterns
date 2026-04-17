from functools import wraps


def log_calls(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print(f"log: calling {func.__name__}")
		return func(*args, **kwargs)

	return wrapper


class ProfileService:
	@log_calls
	def get_profile(self, username: str) -> dict[str, str]:
		return {"username": username, "plan": "starter"}


class AuthorizationProxy:
	def __init__(self, service: ProfileService, allowed_users: set[str]) -> None:
		self.service = service
		self.allowed_users = allowed_users

	def get_profile(self, username: str) -> dict[str, str]:
		if username not in self.allowed_users:
			raise PermissionError("user not allowed")
		return self.service.get_profile(username)


class ProfileFacade:
	def __init__(self, profile_service: AuthorizationProxy) -> None:
		self.profile_service = profile_service

	def load_dashboard(self, username: str) -> str:
		profile = self.profile_service.get_profile(username)
		return f"{profile['username']} -> plan={profile['plan']}"


def main() -> None:
	service = ProfileService()
	proxy = AuthorizationProxy(service, {"ada"})
	facade = ProfileFacade(proxy)
	print(facade.load_dashboard("ada"))


if __name__ == "__main__":
	main()
