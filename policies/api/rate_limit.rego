package topdog.api

# Example OPA policy for simple per-key rate limiting decisions.
# Integrate with a sidecar or gateway that evaluates this policy.

# Input shape (example):
# {
#   "api_key": "abc123",
#   "path": "/api/v1/generate",
#   "method": "POST",
#   "rate": {
#       "requests_per_min": 120
#   }
# }

# Decision: allow or deny
allow {
  not deny
}

deny[msg] {
  input.rate.requests_per_min > limit
  msg := sprintf("rate limit exceeded: %v > %v", [input.rate.requests_per_min, limit])
}

# Default limit; in a real setup this would be loaded from data store per-tenant
limit := 60
