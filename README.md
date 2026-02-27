# Resuable Juju Bundles

This repo contains a collection of useful and commonly used Juju YAML bundles that you can easily deploy in your environment. Most of these bundles can easily be deployed through other methods, such as the [Observability Terraform modules]. Some of these bundles add extra configurations, integrations, etc and are used in specific scenarios.

Some of the bundles here include:

- [Mimir Exemplars]: This bundle deploys Mimir HA along with the Opentelemetry Collector. It enables the storage of exemplars in Mimir. Otelcol is included so that you can test the exemplars feature by sending an exemplar to Mimir through Otelcol. The [Python Exemplars] file can be used for this purpose.

- [Loki and Otelcol over TLS]: This bundle is meant to be used when load testing Otelcol using K6 and relating Otelcol to two units of Loki over TLS. You need to have the K6 binary installed already to be able to load test Otelcol.

- [BE K8s]: the K8s deployment needed to receive logs and metrics from a BE deployed in LXD.
- [BE LXD]: Otelcol, BE, Ubuntu, as well as the SaaS needed to send timeseries from Be to the backend in K8s.

Some of the files here include:

- make_csv.py: Used to get the output of source-wand dependencies and convert the PACKAGE and VERSION into CSV. Use like `python3 make_csv.py input=deptrees/script_exporter/deps.txt output=deptrees/script_exporter/deps.csv`

[Observability Terraform modules]: https://github.com/canonical/observability-stack/tree/main/terraform
[Mimir Exemplars]: https://github.com/sinapah/reusable-juju-bundles/blob/main/mimir-exemplars.py
[Python Exemplars]: https://github.com/sinapah/reusable-juju-bundles/blob/main/mimir-exemplars.py
[Loki and Otelcol over TLS]: https://github.com/sinapah/reusable-juju-bundles/blob/main/my-otel-loki-tls.yaml
