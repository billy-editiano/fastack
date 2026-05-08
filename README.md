# Fastack

Helm charts and conventions for the Fastack monorepo.

This repository contains subcharts for app, worker and mariadb and an umbrella chart used for local testing. The charts follow a small set of conventions to make releases, templating and secret handling predictable.

## Status (what we did so far)
- Standardized service naming using a helper `chart.serviceName` which produces `<fullname>-service` for Services.
- Migrated mariadb to a StatefulSet and consolidated auth into a small, predictable secret model.
- Implemented per-field secret precedence: external secret (per-field) wins; otherwise the chart creates a secret from inline values.
- Added optional `image.registry` support across charts. When empty the templates render `repository:tag`, otherwise `registry/repository:tag`.
- Enabled `tpl` use for templated values (e.g. `database.host`) so values can include templated strings resolved at chart render time.
- Added a CONVENTIONS.md documenting the above rules.

## Conventions (summary)
- Service names: use the helper `chart.serviceName` in templates for Service resources. It yields `{{ include "chart.fullname" . }}-service`.
- Images: values include `image.registry` (optional), `image.repository`, and `image.tag`.
  - If `image.registry` is empty the template emits `repository:tag`.
  - If `image.registry` is set it emits `registry/repository:tag`.
- Database configuration
  - Charts prefer `.Values.database` as the single source of truth for DB env variables.
  - Passwords/auth fields are modeled as objects with three possible fields: `existingSecretName`, `existingSecretKey`, and `value`.
  - Precedence: if `existingSecretName` (and optionally `existingSecretKey`) is provided the chart will mount/read that external secret per-field. Otherwise, if `value` is provided the chart will create an in-chart secret.
  - For mariadb, if both root and user passwords are provided inline the chart creates a single chart-managed auth secret named `<fullname>-auth`.
- Templated values: use `tpl` in chart templates when you expect a values string to contain Helm template expressions (e.g. `database.host: "{{ .Release.Name }}-mariadb-service"`).
- Values preprocessing: values files in this repo may contain Jinja2-style placeholders processed externally. The chosen delimiters are:
  - Comments: [# ... #]
  - Variables: [[ ... ]]
  - Statements: [% ... %]

## Example snippets

MARIADB auth shape (values.yaml)

```yaml
mariadb:
  auth:
    rootPassword:
      existingSecretName: ""
      existingSecretKey: "root"
      value: ""
    password:
      existingSecretName: ""
      existingSecretKey: "password"
      value: ""
```

WORKER database example (values.yaml)

```yaml
worker:
  database:
    host: "{{ .Release.Name }}-mariadb-service"
    port: 3306
    user: fastack
    name: fastack
    password:
      existingSecretName: ""
      existingSecretKey: "password"
      value: ""
```

IMAGE example (values.yaml)

```yaml
image:
  registry: ""        # leave empty to render repository:tag
  repository: myorg/fastack-app
  tag: "0.1.0"
```

## How to render and test locally
- Update umbrella dependencies (when editing subcharts):

  helm dependency update umbrella-test

- Lint a chart:

  helm lint app/helm/chart

- Render templates (dry-run):

  helm template umbrella-test ./umbrella-test -f umbrella-test/values.yaml

- Install/upgrade locally:

  helm upgrade --install umbrella-test ./umbrella-test -f umbrella-test/values.yaml

## Docker Compose builds
- The repository expects `docker-compose.build.yml` files (per-service) to tag build images as `latest`. Check `*/docker-compose.build.yml` if you rely on local builds.

## Key files touched
- CONVENTIONS.md
- app/helm/chart/templates/_helpers.tpl
- worker/helm/chart/templates/_helpers.tpl
- mariadb/helm/chart/templates/_helpers.tpl
- worker/helm/chart/templates/secret.yaml
- mariadb/helm/chart/templates/secret.yaml
- mariadb/helm/chart/templates/statefulset.yaml
- app/helm/chart/templates/deployment.yaml
- umbrella-test/values.yaml

## Next steps / suggestions
1. Wire the app chart to consume `.Values.database.*` (DB env vars + secret precedence) to match worker.
2. Decide whether you want this README committed now (I created the file but did not commit it).
3. Optionally run `helm lint` and `helm template` for each chart and address any Helm warnings.

If you want me to commit this README.md, tell me and I'll create a conventional commit. If you want edits to the README content or a different format, tell me what to change.
