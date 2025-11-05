package topdog.api

default allow = true
reasons := []

# High-risk prompt patterns
unsafe_pattern[p] {
  some p
  patterns := [
    re_match("(?i)ignore\\s+previous\\s+instructions", input.prompt),
    re_match("(?i)drop\\s+database", input.prompt),
    re_match("(?i)exfiltrate|leak\\s+secrets", input.prompt),
    re_match("(?i)(sudo|rm -rf) /", input.prompt),
  ]
  patterns[p]
}

# Tighten for privileged paths or methods
privileged_path {
  startswith(input.path, "/admin")
} else = false

# Decision: deny if unsafe pattern or privileged path without auth
allow {
  not unsafe_pattern[_]
  not (privileged_path and input.headers["x-api-key"] == "")
}

# Provide reasons when denied
reasons := rs {
  rs := [r |
    unsafe_pattern[_]; r := "unsafe_prompt"
  ]
}
