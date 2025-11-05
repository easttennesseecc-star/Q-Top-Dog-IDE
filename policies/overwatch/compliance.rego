package overwatch.compliance

# Example compliance checks; expand per org policy.
# deny[msg] if code or arch proposal violates a rule.

deny[msg] {
  input.resource == "code_snippet"
  contains(input.content, "eval(")
  msg := "disallow eval usage"
}

deny[msg] {
  input.resource == "architecture"
  input.flags.missing_threat_model
  msg := "threat model required"
}
