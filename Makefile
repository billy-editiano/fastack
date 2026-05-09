.PHONY: test

test:
	helm lint umbrella-test -f umbrella-test/values.yaml
	helm template umbrella-test ./umbrella-test -f umbrella-test/values.yaml >/dev/null
