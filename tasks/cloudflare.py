from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import server

from myinfra.facts import brew as brew_facts
from myinfra.facts import cloudflare as cf_facts
from myinfra.operations import cloudflare


@deploy("A Records")
def apply_a_records(zone_id):
    a_records = [
        dict(record="f", value="103.168.172.37"),
        dict(record="f", value="103.168.172.52"),
        dict(record="www", value="192.0.2.1", proxied=True),
    ]
    for r in a_records:
        cloudflare.dns(
            name=f"{'' if r.get('present', True) else 'Remove '}{r['record']}",
            zone_id=zone_id,
            type="A",
            **r,
        )


@deploy("CNAME Records")
def apply_cname_records(zone_id):
    cname_records = [
        ## Cloudflare Pages
        dict(record="@", value="copernicus.pages.dev", proxied=True),
        dict(record="maps", value="mercator.pages.dev", proxied=True),
        dict(record="dash", value="sutra-7zg.pages.dev", proxied=True),
        ## Github Pages
        dict(record="latex", value="activatedgeek.github.io", proxied=True),
        ## Fastmail
        dict(
            record="mesmtp._domainkey",
            value="mesmtp.sanyamkapoor.com.dkim.fmhosted.com",
        ),
        dict(record="fm1._domainkey", value="fm1.sanyamkapoor.com.dkim.fmhosted.com"),
        dict(record="fm2._domainkey", value="fm2.sanyamkapoor.com.dkim.fmhosted.com"),
        dict(record="fm3._domainkey", value="fm3.sanyamkapoor.com.dkim.fmhosted.com"),
        dict(record="mail", value="mail.fastmail.com"),
        ## Goatcounter
        dict(record="gc", value="psiyum.goatcounter.com"),
        dict(record="maps.gc", value="psiyum-maps.goatcounter.com"),
        ## Upptime
        dict(record="status", value="activatedgeek.github.io", proxied=True),
        ## Clerk
        dict(record="clerk.oidc", value="frontend-api.clerk.services"),
        dict(record="accounts.oidc", value="accounts.clerk.services"),
        dict(record="clk._domainkey.oidc", value="dkim1.ddniet4lpbo0.clerk.services"),
        dict(record="clk2._domainkey.oidc", value="dkim2.ddniet4lpbo0.clerk.services"),
        dict(record="clkmail.oidc", value="mail.ddniet4lpbo0.clerk.services"),
    ]
    for r in cname_records:
        cloudflare.dns(
            name=f"{'' if r.get('present', True) else 'Remove '}{r['record']}",
            zone_id=zone_id,
            zone_name="sanyamkapoor.com",
            type="CNAME",
            **r,
        )


@deploy("MX Records")
def apply_mx_records(zone_id):
    mx_records = [
        dict(record="@", value="in1-smtp.messagingengine.com", priority=10),
        dict(record="@", value="in2-smtp.messagingengine.com", priority=20),
    ]
    for r in mx_records:
        cloudflare.dns(
            name=f"{'' if r.get('present', True) else 'Remove '}{r['record']}",
            zone_id=zone_id,
            zone_name="sanyamkapoor.com",
            type="MX",
            **r,
        )


@deploy("SRV Records")
def apply_srv_records(zone_id):
    srv_records = [
        dict(record="_submission._tcp", priority=0, value="1 587 smtp.fastmail.com"),
        dict(record="_imap._tcp", priority=0, value="0 993 imap.fastmail.com"),
        dict(record="_imaps._tcp", priority=0, value="1 993 imap.fastmail.com"),
        dict(record="_pop3._tcp", priority=10, value="0 995 pop.fastmail.com"),
        dict(record="_pop3s._tcp", priority=10, value="1 995 pop.fastmail.com"),
        dict(record="_jmap._tcp", priority=0, value="1 443 api.fastmail.com"),
        dict(
            record="_autodiscover._tcp",
            priority=0,
            value="1 443 autodiscover.fastmail.com",
        ),
    ]
    for r in srv_records:
        cloudflare.dns(
            name=f"{'' if r.get('present', True) else 'Remove '}{r['record']}",
            zone_id=zone_id,
            type="SRV",
            **r,
        )


@deploy("TXT Records")
def apply_txt_records(zone_id):
    txt_records = [
        dict(record="@", value="v=spf1 include:spf.messagingengine.com ?all"),
        dict(record="_dmarc", value="v=DMARC1; p=none;"),
        dict(record="_atproto", value="did=did:plc:r65ialxtka33wyid523oipsk"),
    ]
    for r in txt_records:
        cloudflare.dns(
            name=f"{'' if r.get('present', True) else 'Remove '}{r['record']}",
            zone_id=zone_id,
            zone_name="sanyamkapoor.com",
            type="TXT",
            **r,
        )


@deploy("Backup")
def apply_backup(zone_id, teardown=False):
    ## Backup everyday at 6pm.
    server.crontab(
        name="Zone File",
        command=f'export SHELL={host.get_fact(brew_facts.BrewPrefix)}/bin/bash; source ~/.local/profile/.bash_env; curl --request GET --url https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/export --header "Content-Type: application/json" --header "X-Auth-Email: {host.data.cloudflare_email}" --header "X-Auth-Key: ${{CLOUDFLARE_API_KEY}}" -o {host.data.backup_dir}/sanyamkapoor.com.zone >>/tmp/zone-export.cf.log 2>&1',
        minute="0",
        hour="*/18",
        month="*",
        day_of_week="*",
        day_of_month="*",
        present=not teardown,
    )


@deploy("Cloudflare")
def apply(teardown=False):
    zone_id = host.get_fact(cf_facts.Zone, "sanyamkapoor.com")

    if host.data.get("apply_dns", False):
        apply_a_records(zone_id)

        apply_cname_records(zone_id)

        apply_mx_records(zone_id)

        apply_srv_records(zone_id)

        apply_txt_records(zone_id)

    apply_backup(zone_id, teardown=teardown)


if all([host.data.get(k, "") for k in ["cloudflare_email", "cloudflare_api_key"]]):
    apply()
