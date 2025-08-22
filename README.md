# Resuable Juju Bundles

This repo contains a collection of useful and commonly used Juju YAML bundles that you can easily deploy in your environment. Most of these bundles can easily be deployed through other methods, such as the [Observability Terraform modules]. Some of these bundles add extra configurations, integrations, etc and are used in specific scenarios.

Some of the bundles here include:

- [Mimir Exemplars]: This bundle deploys Mimir HA along with the Opentelemetry Collector. It enables the storage of exemplars in Mimir. Otelcol is included so that you can test the exemplars feature by sending an exemplar to Mimir through Otelcol. The [Python Exemplars] file can be used for this purpose.

[Observability Terraform modules]: https://github.com/canonical/observability-stack/tree/main/terraform
[Mimir Exemplars]: https://github.com/sinapah/reusable-juju-bundles/blob/main/mimir-exemplars.py
[Python Exemplars]: https://github.com/sinapah/reusable-juju-bundles/blob/main/mimir-exemplars.py
