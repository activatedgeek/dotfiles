from myinfra.facts import cloudflare as cf_facts
from myinfra.operations import cloudflare
from myinfra.operations import files as myfiles
from pyinfra.api import deploy
from pyinfra.facts import launchd as launchd_facts
from pyinfra.facts import server as server_facts
from pyinfra.operations import files, server

from pyinfra import host


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
    remote_home = host.get_fact(server_facts.Home)

    service_label = "com.sanyamkapoor.cloudflare"
    plist_path = f"{remote_home}/Library/LaunchAgents/{service_label}.plist"
    backup_dir = host.data.backup_dir.replace("~/", f"{remote_home}/", 1).replace("\\ ", " ")

    service_loaded = service_label in host.get_fact(launchd_facts.LaunchdStatus)
    if teardown and service_loaded:
        server.shell(
            name="Bootout LaunchAgent",
            commands=f'launchctl bootout "gui/$(id -u)/{service_label}"',
        )

    if not teardown:
        files.directory(name="LaunchAgents Directory", path=f"{remote_home}/Library/LaunchAgents", mode=700)

    files.directory(
        name=f"{'Remove ' if teardown else ''}Log Directory",
        path=f"{remote_home}/Library/Logs/Cloudflare",
        mode=700,
        present=not teardown,
    )

    launch_agent = myfiles.template(
        name=f"{'Remove ' if teardown else ''}LaunchAgent",
        src="tasks/cloudflare/templates/com.sanyamkapoor.cloudflare.plist.j2",
        dest=plist_path,
        mode=600,
        present=not teardown,
        stdout_path=f"{remote_home}/Library/Logs/Cloudflare/launchctl-export.log",
        cloudflare_api_key=host.data.cloudflare_api_key,
        zone_id=zone_id,
        cloudflare_email=host.data.cloudflare_email,
        backup_path=f"{backup_dir}/sanyamkapoor.com.zone",
    )

    if not teardown:
        server.shell(
            name="Bootstrap LaunchAgent",
            commands=[
                f'plutil -lint "{plist_path}"',
                f'launchctl bootout "gui/$(id -u)/{service_label}" >/dev/null 2>&1 || true',
                f'launchctl bootstrap "gui/$(id -u)" "{plist_path}"',
            ],
            _if=lambda: launch_agent.did_change() or not service_loaded,
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

    if "home" in host.groups:
        apply_backup(zone_id, teardown=teardown)


def pre_check():
    return all([host.data.get(k, "") for k in ["cloudflare_email", "cloudflare_api_key"]])
