module "cos" {
  source                          = "git::https://github.com/canonical/observability-stack//terraform/cos?ref=54108f1e5a5fa4eadc71066f4d5248fd83df6099"  # 21/Jul/2025
  model                           = "cos-ha" # or whatever model name
  channel                         = "2/edge"
  anti_affinity                   = false
  internal_tls                    = false
  external_certificates_offer_url = null
  s3_endpoint                     = "http://$IPADDR:8080"
  s3_secret_key                   = "secret-key"
  s3_access_key                   = "access-key"
  loki_bucket                     = "loki"
  mimir_bucket                    = "mimir"
  tempo_bucket                    = "tempo"
  s3_integrator                   = { channel = "2/edge", revision = 157 }  # FIXME: https://github.com/canonical/observability/issues/342
  ssc                             = { channel = "1/stable" }
  traefik                         = { channel = "latest/stable" }
}
/*
Before this can work, make sure you've done: 
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')

# Ref: https://canonical-microceph.readthedocs-hosted.com/en/latest/tutorial/get-started/
echo "Setting up microceph..."
microceph cluster bootstrap
microceph disk add loop,4G,3
ceph status

# Ref: https://canonical-microceph.readthedocs-hosted.com/en/latest/reference/commands/enable/#rgw
# (Traefik will take ports 80, 443)
microceph enable rgw --port 8080 --ssl-port 8443
microceph.ceph -s
microceph.radosgw-admin user create --uid=user --display-name=User
microceph.radosgw-admin key create --uid=user --key-type=s3 --access-key=access-key --secret-key=secret-key

and
for BUCKET in loki mimir tempo; do
  s3cmd --host=$IPADDR:8080 \
    --access_key=access-key \
    --secret_key=secret-key \
    --host-bucket= \
    --no-ssl \
    mb s3://$BUCKET
done 
*/