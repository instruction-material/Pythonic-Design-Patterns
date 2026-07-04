from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar


#################
#   CONSTANTS   #
#################

SAMPLE_USERNAME = "ada"
SAMPLE_PLAN = "pro"
SAMPLE_STATUS = "active"
SAMPLE_BILLING_STATUS = "paid"
ALLOWED_USERS = {SAMPLE_USERNAME}


#############
#   TYPES   #
#############

PARAMS = ParamSpec("PARAMS")
RETURN_TYPE = TypeVar("RETURN_TYPE")


#################
#   FUNCTIONS   #
#################

def log_calls(
	func: Callable[PARAMS, RETURN_TYPE],
) -> Callable[PARAMS, RETURN_TYPE]:
	"""Log each call to the decorated function"""
	# Wrap the function while preserving its metadata
	@wraps(func)
	def wrapper(*args: PARAMS.args, **kwargs: PARAMS.kwargs) -> RETURN_TYPE:
		"""Print a log line and call the wrapped function"""
		print(f"log: calling {func.__name__}")
		return func(*args, **kwargs)

	return wrapper


def cache_result(
	func: Callable[PARAMS, RETURN_TYPE],
) -> Callable[PARAMS, RETURN_TYPE]:
	"""Cache results by positional and keyword arguments"""
	cache: dict[
		tuple[tuple[object, ...], tuple[tuple[str, object], ...]],
		RETURN_TYPE,
	] = {}

	# Wrap the function with a small in-memory cache
	@wraps(func)
	def wrapper(*args: PARAMS.args, **kwargs: PARAMS.kwargs) -> RETURN_TYPE:
		"""Return a cached result when possible"""
		key = (args, tuple(sorted(kwargs.items())))

		# Store the result the first time this argument set appears
		if key not in cache:
			cache[key] = func(*args, **kwargs)

		return cache[key]

	return wrapper


#############
#   TYPES   #
#############

# Load profile data for one user
class ProfileService:
	"""Provide profile data from the core service"""

	@cache_result
	@log_calls
	def get_profile(self, username: str) -> dict[str, str]:
		"""Return profile data for one username"""
		return {
			"username": username,
			"plan": SAMPLE_PLAN,
			"status": SAMPLE_STATUS,
		}


# Guard profile access before delegating to the service
class AuthorizationProxy:
	"""Authorize users before profile data is loaded"""

	def __init__(self, service: ProfileService, allowed_users: set[str]) -> None:
		"""Store the wrapped service and allowed usernames"""
		self.service = service
		self.allowed_users = allowed_users

	def get_profile(self, username: str) -> dict[str, str]:
		"""Return a profile only when the user is allowed"""
		# Reject users outside the proxy allowlist
		if username not in self.allowed_users:
			raise PermissionError("user not allowed")

		return self.service.get_profile(username)


# Load billing information for one user
class BillingService:
	"""Provide billing data for the dashboard"""

	def get_balance(self, username: str) -> str:
		"""Return the billing status for one username"""
		return SAMPLE_BILLING_STATUS


# Combine profile and billing services behind one interface
class ProfileFacade:
	"""Load dashboard data through a simple facade"""

	def __init__(
		self,
		profile_service: AuthorizationProxy,
		billing_service: BillingService,
	) -> None:
		"""Store services used by the facade"""
		self.profile_service = profile_service
		self.billing_service = billing_service

	def load_dashboard(self, username: str) -> str:
		"""Return the combined dashboard summary"""
		profile = self.profile_service.get_profile(username)
		balance = self.billing_service.get_balance(username)
		return (
			f"{profile['username']} -> plan={profile['plan']} "
			f"status={profile['status']} billing={balance}"
		)


#################
#   MAIN CODE   #
#################

def main() -> None:
	"""Build the facade and load the same dashboard twice"""
	service = ProfileService()
	proxy = AuthorizationProxy(service, ALLOWED_USERS)
	facade = ProfileFacade(proxy, BillingService())
	print(facade.load_dashboard(SAMPLE_USERNAME))
	print(facade.load_dashboard(SAMPLE_USERNAME))


if __name__ == "__main__":
	main()
