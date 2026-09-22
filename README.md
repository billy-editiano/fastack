# Fastack

Helm charts and conventions for the Fastack monorepo.

This repository contains subcharts for app, worker and mariadb and an umbrella chart used for local testing. The charts follow a small set of conventions to make releases, templating and secret handling predictable.

## Status (what we did so far)
- Standardized service naming using a helper `chart.serviceName` which produces `<fullname>-service` for Services.
- Migrated mariadb to a StatefulSet and consolidated auth into a small, predictable secret model.
- Implemented per-field secret precedence: external secret (per-field) wins; otherwise the chart creates a secret from inline values.
- Added optional `image.registry` support across charts. When empty the templates render `repository:tag`, otherwise `registry/repository:tag`.
- Enabled `tpl` use for templated values (e.g. `database.host`) so values can include templated strings resolved at chart render time.
- Aligned worker and mariadb values paths with the templates that consume them.
- Added an explicit PVC template for mariadb persistence.
- Added a CONVENTIONS.md documenting the above rules.

## Conventions (summary)
- Service names: use the helper `chart.serviceName` in templates for Service resources. It yields `{{ include "chart.fullname" . }}-service`.
- Images: values include `image.registry` (optional), `image.repository`, and `image.tag`.
  - If `image.registry` is empty the template emits `repository:tag`.
  - If `image.registry` is set it emits `registry/repository:tag`.
- Database configuration
  - Worker-like charts prefer top-level `.Values.database` as the source of truth for DB env variables.
  - MariaDB-like charts use top-level `.Values.auth` for runtime auth settings.
  - Passwords/auth fields are modeled as objects with three possible fields: `existingSecretName`, `existingSecretKey`, and `value`.
  - Precedence: if `existingSecretName` (and optionally `existingSecretKey`) is provided the chart will mount/read that external secret per-field. Otherwise, if `value` is provided the chart will create an in-chart secret.
  - For mariadb, if both root and user passwords are provided inline the chart creates a single chart-managed auth secret named `<fullname>-auth`.
  - If mariadb persistence is enabled, the chart also creates the PVC it mounts.
- Templated values: use `tpl` in chart templates when you expect a values string to contain Helm template expressions (e.g. `database.host: "{{ .Release.Name }}-mariadb-service"`).
- Values preprocessing: values files in this repo may contain Jinja2-style placeholders processed externally. The chosen delimiters are:
  - Comments: [# ... #]
  - Variables: [[ ... ]]
  - Statements: [% ... %]

## Example snippets

MARIADB auth shape (values.yaml)

```yaml
auth:
  rootPassword:
    existingSecretName: null
    existingSecretKey: null
    value: rootpassword
  database: appdb
  user: appuser
  password:
    existingSecretName: null
    existingSecretKey: null
    value: apppassword
```

WORKER database example (values.yaml)

```yaml
database:
  host: "{{ .Release.Name }}-mariadb-service"
  port: 3306
  user: appuser
  name: appdb
  password:
    existingSecretName: null
    existingSecretKey: null
    value: apppassword
```

IMAGE example (values.yaml)

```yaml
image:
  registry: ""        # leave empty to render repository:tag
  repository: fastack/app
  tag: latest
```

## Helm: render and test locally
- Update umbrella dependencies (when editing subcharts):

  helm dependency update umbrella-test

- Lint a chart:

  helm lint app/helm/chart

- Render templates (dry-run):

  helm template umbrella-test ./umbrella-test -f umbrella-test/values.yaml

- Install/upgrade locally:

  helm upgrade --install umbrella-test ./umbrella-test -f umbrella-test/values.yaml

## Docker Swarm deployment
- Each participating artifact owns its Swarm fragment at
  `artifact/swarm/stack.yml`. The current fragments are
  `app/swarm/stack.yml`, `worker/swarm/stack.yml`, and
  `mariadb/swarm/stack.yml`.
- Umbrella Packager merges those fragments into one generated
  `swarm-stack.yml`; there is no root deployment artifact or root
  `swarm/stack.yml`.
- Fragments must reference published, immutable release images through
  `published_image(...)`, rather than local `fastack/*:latest` build tags.
- The shared `fastack` overlay network may be declared by each fragment when
  the definitions are identical. The `mariadb` fragment owns the
  `mariadb-data` named volume.
- The literal database credentials in these fragments are development-only
  demonstration values. Production releases should use externally managed
  Swarm secrets instead of embedding credentials in service environments.
- Swarm stacks do not provide Docker Compose startup ordering; services must tolerate their dependencies becoming available later.
- Packaging produces the deployment artifact only. Deploy the extracted stack externally:

  ```bash
  docker stack deploy --with-registry-auth --compose-file swarm-stack.yml fastack
  ```

## Docker Compose builds
- The repository expects `docker-compose.build.yml` files (per-service) to tag build images as `latest`. Check `*/docker-compose.build.yml` if you rely on local builds.
- `umbrella.docker-compose.yml` is a separate local-development file. Its `build` and `depends_on` entries do not belong in packaged Swarm fragments.

## Key files touched
- CONVENTIONS.md
- app/helm/chart/templates/_helpers.tpl
- worker/helm/chart/templates/_helpers.tpl
- mariadb/helm/chart/templates/_helpers.tpl
- worker/helm/chart/templates/secret.yaml
- mariadb/helm/chart/templates/secret.yaml
- mariadb/helm/chart/templates/statefulset.yaml
- mariadb/helm/chart/templates/persistentvolumeclaim.yaml
- app/helm/chart/templates/deployment.yaml
- umbrella-test/values.yaml

## Next steps / suggestions
1. Optionally add app-side database wiring only if the app actually needs runtime DB configuration.
2. Run `helm lint` for each chart and `helm template` for `umbrella-test` after chart edits.
