# Conventions

## Repo Layout
- Each service lives in its own top-level directory: `app/`, `worker/`, `mariadb/`.
- Each service directory contains application code plus build/deployment artifacts.
- The shared umbrella test lives in `umbrella-test/`.

## Naming
- Services use `{{ include "chart.serviceName" . }}`.
- `chart.serviceName` is derived from `chart.fullname` and appends `-service`.
- `nameOverride` and `fullnameOverride` are always explicit values in `values.yaml`.

## Helm Layout
- Helm charts live under `service/helm/chart/`.
- Chart metadata is in `service/helm/chart/Chart.yaml`.
- Templates are in `service/helm/chart/templates/`.
- Chart defaults are in `service/helm/chart/values.yaml`.
- Sample install values are in `service/helm/values.sample.yaml`.
- Service-specific chart helpers should stay in `service/helm/chart/templates/_helpers.tpl`.

## Docker Swarm Layout
- Each participating service owns `service/swarm/stack.yml`, separate from its Helm chart.
- Umbrella Packager merges the participating fragments into one generated `swarm-stack.yml`; there is no root Swarm stack owner.
- Fragments must reference published, immutable release images with `published_image(...)`, not local `fastack/*:latest` build tags.
- Shared resources may be repeated only when their definitions are identical. The `fastack` overlay network is shared by all fragments, while `mariadb-data` is owned by `mariadb/swarm/stack.yml`.
- File-backed configs, when added, must live under the owning service's `swarm/assets/` directory and are packaged under an artifact-scoped destination.
- The literal database credentials in the example fragments are development-only. Production deployments should use externally managed Swarm secrets.
- Do not depend on Docker Compose startup ordering in the stack; services must handle dependencies becoming available later.
- Packaging does not deploy the stack. Deploy the packaged artifact externally.

## Templated Values
- Values that point to other Kubernetes names or DNS targets may contain Helm templates.
- These fields must be rendered with `tpl` in templates.
- Current convention: `database.host` is templated.
- Keep templated values limited to infrastructure references, not arbitrary app config.
- Prefer `"{{ .Release.Name }}-<service>-service"` for cross-chart Service DNS defaults.
- Chart values files support Jinja2-style templating for the external post-processor.
- The supported delimiters are `[# comments #]`, `[[ variables ]]`, and `[% statements %]`.
- This applies to both `values.yaml` and `values.sample.yaml`.
- Helm templates should treat these as plain strings unless they are explicitly rendered with `tpl`.

## Images
- `image.registry` is optional and defaults to an empty string.
- If `image.registry` is empty, the final image should render as `repository:tag`.
- If `image.registry` is set, render `registry/repository:tag`.
- Keep `repository`, `tag`, and `pullPolicy` as the standard image fields.
- Service-local chart defaults should keep `registry` and `repository` separate instead of folding the registry into `repository`.
- Local umbrella-test values may keep `registry: ""` and use `fastack/<service>` repositories with `tag: latest`.

## Database
- Prefer service DNS names over hardcoded IPs.
- Default database host values should resolve from release context when the chart is rendered.
- Cross-chart database settings should stay in chart values, not inline in templates.
- Worker-like services keep database config under top-level `database:`.
- MariaDB auth supports per-field `existingSecretName` / `existingSecretKey` / `value`.
- If inline `value` is provided for both MariaDB passwords, create one chart secret containing both.
- External secrets win per field when provided.
- MariaDB-like services keep auth config under top-level `auth:`.
- `auth.database` and `auth.user` remain plain values; only passwords participate in secret selection.
- If persistence is enabled for MariaDB, the chart must create the PVC it mounts.

## Build and Umbrella Files
- Each service has a `docker-compose.build.yml` for local image builds.
- `docker-compose.build.yml` should always tag the image(s) as `latest`.
- Each service has an `umbrella-service.yml` for image/dependency metadata used by the umbrella pipeline.
- Add this note to `umbrella-service.yml`: `Please refer to Umbrella Builder notion page for more information`.
- These files should remain aligned with the service name and image name in that directory.
- Current service image names are `fastack/app`, `fastack/worker`, and `fastack/mariadb`.
- Each Swarm service fragment must define a non-empty `services` mapping and must not include Compose build-only fields such as `build` or `depends_on`.
