from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.command import StringCommand
from cloudflare import Cloudflare

from ..facts import cloudflare as cf_facts

client = Cloudflare(
    api_email=host.data.cloudflare_email,
    api_key=host.data.cloudflare_api_key,
)


@operation()
def dns(
    zone_id,
    type,
    record,
    value,
    zone_name=None,
    proxied=False,
    ttl=1,
    priority=None,
    present=True,
):
    dns_record_id = host.get_fact(
        cf_facts.DNSRecord,
        zone_id=zone_id,
        zone_name=zone_name,
        type=type,
        record=record,
        value=value,
    )

    if dns_record_id:
        if present:
            dns_record = client.dns.records.get(
                dns_record_id=dns_record_id, zone_id=zone_id
            )

            is_match = (dns_record.proxied == proxied) and (dns_record.ttl == ttl)
            try:
                is_match = is_match and (dns_record.priority == priority)
            except AttributeError:
                pass

            if not is_match:
                client.dns.records.update(
                    dns_record_id=dns_record_id,
                    zone_id=zone_id,
                    content=value,
                    name=record,
                    type=type,
                    proxied=proxied,
                    ttl=ttl,
                    ## FIXME: other attributes?
                )
                yield StringCommand("true")
        else:
            client.dns.records.delete(dns_record_id=dns_record_id, zone_id=zone_id)
            yield StringCommand("true")
    else:
        if present:
            client.dns.records.create(
                zone_id=zone_id,
                content=value,
                name=record,
                type=type,
                proxied=proxied,
                ttl=ttl,
                ## FIXME: other attributes?
            )
            yield StringCommand("true")
