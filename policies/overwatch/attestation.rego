package overwatch.attestation

# Require three-part attestation before deploy
# data_attested: dataset signature verified
# code_attested: training code hash verified
# policy_attested: checks against policy bundle

deny[msg] {
  input.resource == "model_release"
  not input.attestations.data_attested
  msg := "training dataset not attested"
}

deny[msg] {
  input.resource == "model_release"
  not input.attestations.code_attested
  msg := "training code not attested"
}

deny[msg] {
  input.resource == "model_release"
  not input.attestations.policy_attested
  msg := "policy checks not attested"
}
