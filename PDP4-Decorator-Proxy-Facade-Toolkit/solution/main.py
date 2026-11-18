"""Transparent wrappers, authorized cached access and a dashboard facade."""
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from functools import wraps
import inspect
from threading import RLock
from typing import ParamSpec, Protocol, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    """Keep callable shape, metadata, arguments, results and failure behavior."""
    if inspect.isasyncgenfunction(func):
        @wraps(func)
        async def asynchronous_generator(*args: P.args, **kwargs: P.kwargs) -> AsyncGenerator[object, object]:
            print(f"log: calling {func.__name__}")
            inner = cast(AsyncGenerator[object, object], func(*args, **kwargs))
            try:
                value = await inner.__anext__()
                while True:
                    try:
                        incoming = yield value
                    except GeneratorExit:
                        await inner.aclose()
                        raise
                    except BaseException as error:
                        value = await inner.athrow(error)
                    else:
                        value = await inner.asend(incoming)
            except StopAsyncIteration:
                return
            finally:
                await inner.aclose()
        return cast(Callable[P, R], asynchronous_generator)
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def asynchronous(*args: P.args, **kwargs: P.kwargs) -> object:
            print(f"log: calling {func.__name__}")
            return await cast(Awaitable[object], func(*args, **kwargs))
        return cast(Callable[P, R], asynchronous)
    if inspect.isgeneratorfunction(func):
        @wraps(func)
        def generator(*args: P.args, **kwargs: P.kwargs) -> Generator[object, object, object]:
            print(f"log: calling {func.__name__}")
            return (yield from cast(Generator[object, object, object], func(*args, **kwargs)))
        return cast(Callable[P, R], generator)

    @wraps(func)
    def synchronous(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"log: calling {func.__name__}")
        return func(*args, **kwargs)
    return synchronous


def cache_result(func: Callable[P, R]) -> Callable[P, R]:
    """Memoize synchronous value calls, with bound/default-normalized keys.

    Bound values must be hashable. Variable keyword items are sorted. One
    reentrant lock serializes misses and invalidation, including computation.
    Successful results are retained by identity; exceptions are never cached.
    Coroutine and generator functions require a different lifetime policy.
    """
    if (inspect.iscoroutinefunction(func) or inspect.isgeneratorfunction(func)
            or inspect.isasyncgenfunction(func)):
        raise TypeError("cache_result requires a synchronous value function")
    signature = inspect.signature(func)
    cache: dict[tuple[tuple[str, object], ...], R] = {}
    lock = RLock()

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        parts: list[tuple[str, object]] = []
        for name, value in bound.arguments.items():
            if signature.parameters[name].kind is inspect.Parameter.VAR_KEYWORD:
                value = tuple(sorted(cast(dict[str, object], value).items()))
            parts.append((name, value))
        key = tuple(parts)
        hash(key)
        with lock:
            if key not in cache:
                value = func(*args, **kwargs)
                # A dynamically misdeclared function may return a coroutine.
                if inspect.iscoroutine(value):
                    value.close()
                    raise TypeError("cache_result does not cache coroutines")
                if inspect.isawaitable(value) or inspect.isgenerator(value) or inspect.isasyncgen(value):
                    raise TypeError("cache_result does not cache deferred computations")
                cache[key] = value
            return cache[key]

    def clear() -> None:
        with lock:
            cache.clear()

    setattr(wrapper, "cache_clear", clear)
    return wrapper


def clear_cache(func: object) -> None:
    clear = getattr(func, "cache_clear", None)
    if not callable(clear):
        raise TypeError("function does not expose cache_clear")
    cast(Callable[[], None], clear)()


def require_username(username: str) -> str:
    if not isinstance(username, str):
        raise TypeError("username must be a string")
    if not username.strip():
        raise ValueError("username must contain a non-space character")
    return username


class ProfileReader(Protocol):
    def get_profile(self, username: str) -> dict[str, str]: ...


class BillingReader(Protocol):
    def get_balance(self, username: str) -> str: ...


class ProfileService:
    def __init__(self) -> None:
        self.loads = 0

    @log_calls
    def get_profile(self, username: str) -> dict[str, str]:
        """Load a supplied profile; this classroom service performs no network I/O."""
        require_username(username)
        self.loads += 1
        return {"username": username, "plan": "pro", "status": "active"}


class AuthorizationProxy:
    """Guard access, then delegate memoization to a reusable value decorator."""
    def __init__(self, service: ProfileReader, allowed_users: set[str]) -> None:
        self.service = service
        self.allowed_users = {require_username(name) for name in allowed_users}
        self._cached = cache_result(self._load_owned)
        self._lock = RLock()

    def _load_owned(self, username: str) -> dict[str, str]:
        return dict(self.service.get_profile(username))

    def get_profile(self, username: str) -> dict[str, str]:
        require_username(username)
        with self._lock:
            if username not in self.allowed_users:
                raise PermissionError("user not allowed")
            return dict(self._cached(username))

    def invalidate(self) -> None:
        with self._lock:
            clear_cache(self._cached)


class BillingService:
    def get_balance(self, username: str) -> str:
        require_username(username)
        return "paid"


class ProfileFacade:
    """Translate two service results into one complete dashboard value."""
    def __init__(self, profile_service: ProfileReader,
                 billing_service: BillingReader | None = None) -> None:
        self.profile_service = profile_service
        self.billing_service = BillingService() if billing_service is None else billing_service

    def load_dashboard(self, username: str) -> str:
        profile = self.profile_service.get_profile(username)
        balance = self.billing_service.get_balance(username)
        return (f"{profile['username']} -> plan={profile['plan']} "
                f"status={profile['status']} billing={balance}")


def main() -> None:
    service = ProfileService()
    proxy = AuthorizationProxy(service, {"ada"})
    facade = ProfileFacade(proxy, BillingService())
    print(facade.load_dashboard("ada"))
    print(facade.load_dashboard("ada"))


if __name__ == "__main__":
    main()
