import uuid
from locust import FastHttpUser, task, between


class StressTestUser(FastHttpUser):
    # Minimal wait time to simulate extreme, aggressive load (bottleneck identification)
    wait_time = between(0.1, 0.5)

    @task(3)
    def tenant_login_invalid(self):
        """
        Target: /v1.0/auth/tenant/login
        Causes heavy CPU load due to dummy Argon2 hashing and database queries.
        The goal is to push the system until it drops requests, returns 500s, or rate limits aggressively.
        """
        random_email = f"stresstest_{uuid.uuid4().hex[:8]}@example.com"

        with self.client.post(
            "/v1.0/auth/tenant/login",
            json={"email": random_email, "password": "stresstest_password"},
            catch_response=True,
        ) as response:
            # Accept a wide range of status codes as "success" since we *want* to observe failure behaviors
            if response.status_code in [401, 429, 500, 502, 503]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def check_health(self):
        """
        Target: /health
        Checks if the server remains responsive during the CPU spike.
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Healthcheck failed: {response.status_code}")
