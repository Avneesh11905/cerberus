import uuid
from locust import FastHttpUser, task, between, events


class LoadTestUser(FastHttpUser):
    # Moderate wait time to simulate standard sustained load
    wait_time = between(1, 3)

    @task
    def tenant_login_invalid(self):
        """
        Target: /v1.0/auth/tenant/login
        We intentionally use random, invalid emails. In Cerberus, if a user is not found,
        the system executes `await hasher.dummy_verify()` which simulates a full Argon2
        hash calculation (~200ms) to prevent timing attacks.

        This perfectly simulates a heavy, CPU-bound authentication load.
        """
        random_email = f"loadtest_{uuid.uuid4().hex[:8]}@example.com"

        with self.client.post(
            "/v1.0/auth/tenant/login",
            json={"email": random_email, "password": "loadtest_password"},
            catch_response=True,
        ) as response:
            # We expect a 401 Unauthorized (Invalid Credentials).
            # A 429 Too Many Requests is also expected if the IP rate limit is hit.
            if response.status_code in [401, 429]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


@events.quitting.add_listener
def assert_stats(environment, **kwargs):
    """
    Quality Gate Assertion: Fails the CI pipeline if latency thresholds are breached.
    """
    if environment.stats.total.num_requests == 0:
        return

    p95_latency = environment.stats.total.get_response_time_percentile(0.95)
    fail_ratio = environment.stats.total.fail_ratio

    print("\n--- Load Test Assertions ---")
    print(f"P95 Latency: {p95_latency} ms")
    print(f"Fail Ratio: {fail_ratio * 100:.2f}%")

    failed = False

    # Assert p95 latency is under 300ms (Argon2 takes ~200ms, plus network/DB overhead)
    if p95_latency > 300:
        print(f"❌ FAILED: P95 Latency of {p95_latency}ms exceeded 300ms threshold.")
        failed = True

    # Fail if the API returned unexpected status codes (e.g. 500 Internal Server Error)
    if fail_ratio > 0.05:
        print(
            f"❌ FAILED: Fail ratio of {fail_ratio * 100:.2f}% exceeded 5% threshold."
        )
        failed = True

    if failed:
        environment.process_exit_code = 1
    else:
        print("✅ PASSED: All load test criteria met.")
