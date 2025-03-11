from cloudflare import Cloudflare
from pyinfra import host
from pyinfra.api.facts import FactBase
from pyinfra.api.exceptions import FactError


client = Cloudflare(
    api_email=host.data.cloudflare_email,
    api_key=host.data.cloudflare_api_key,
)


class Zone(FactBase):
    def command(self, zone):
        result = client.zones.list(name=zone).result
        if len(result) != 1:
            raise FactError(f"Zone '{zone}' not found")

        return f"echo {result[0].id}"

    def process(self, output):
        return "".join(output).strip()


class DNSRecord(FactBase):
    def command(self, zone_id, type, record, value, zone_name=None):
        results = client.dns.records.list(
            match="any",
            type=type,
            zone_id=zone_id,
            name=record,
            content=value,
        ).result

        results = [
            r
            for r in results
            if (r.type == type)
            and (r.name == zone_name if record == "@" else r.name.startswith(record))
            and (r.content == value)
        ]

        if len(results) == 1:
            return f"echo {results[0].id}"

        return "echo"

    def process(self, output):
        return "".join(output).strip() or None
