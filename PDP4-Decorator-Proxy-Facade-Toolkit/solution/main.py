from functools import wraps


def log_calls(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print(f"log: calling {func.__name__}")
		return func(*args, **kwargs)

	return wrapper


def cache_result(func):
	cache: dict[tuple[tuple[object, ...], tuple[tuple[str, object], ...]], object] = {}

	@wraps(func)
	def wrapper(*args, **kwargs):
		key = (args, tuple(sorted(kwargs.items())))
		if key not in cache:
			cache[key] = func(*args, **kwargs)
		return cache[key]

	return wrapper


class ProfileService:
	@cache_result
	@log_calls
	def get_profile(self, username: str) -> dict[str, str]:
		return {"username": username, "plan": "pro", "status": "active"}


class AuthorizationProxy:
	def __init__(self, service: ProfileService, allowed_users: set[str]) -> None:
		self.service = service
		self.allowed_users = allowed_users

	def get_profile(self, username: str) -> dict[str, str]:
		if username not in self.allowed_users:
			raise PermissionError("user not allowed")
		return self.service.get_profile(username)


class BillingService:
	def get_balance(self, username: str) -> str:
		return "paid"


class ProfileFacade:
	def __init__(
		self,
		profile_service: AuthorizationProxy,
		billing_service: BillingService,
	) -> None:
		self.profile_service = profile_service
		self.billing_service = billing_service

	def load_dashboard(self, username: str) -> str:
		profile = self.profile_service.get_profile(username)
		balance = self.billing_service.get_balance(username)
		return (
			f"{profile['username']} -> plan={profile['plan']} "
			f"status={profile['status']} billing={balance}"
		)


def main() -> None:
	service = ProfileService()
	proxy = AuthorizationProxy(service, {"ada"})
	facade = ProfileFacade(proxy, BillingService())
	print(facade.load_dashboard("ada"))
	print(facade.load_dashboard("ada"))


if __name__ == "__main__":
	main()
