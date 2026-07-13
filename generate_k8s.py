#!/usr/bin/env python3
"""
k8s-generator
=============
Doc cac file mau (.tpl) trong thu muc templates/, thay the placeholder
dang {{TEN_BIEN}} bang gia tri thuc te, roi ghi ra file YAML hoan chinh.

Cau truc thu muc:

  k8s-generator/
    generate_k8s.py          <- script nay
    templates/
      deployment.yaml.tpl
      service.yaml.tpl
      configmap.yaml.tpl
      hpa.yaml.tpl
      ingress.yaml.tpl
      _ingress_rule.yaml.tpl   (mau con, lap lai cho tung service)
      _volume_mounts.yaml.tpl  (mau con, chen vao deployment neu can PVC logs)
      _volumes.yaml.tpl        (mau con, chen vao deployment neu can PVC logs)
      pvc.yaml.tpl
      secret.yaml.tpl
    example-services.yaml     <- vi du file cau hinh nhieu service

Muon doi khuon mau (them field, doi resources mac dinh, doi annotation
ingress...) chi can SUA FILE .tpl, khong can dong vao code Python.

Cach dung:

  1) Tuong tac (chi can nhap ten):
       python3 generate_k8s.py

  2) Dong lenh:
       python3 generate_k8s.py --project b2b \\
         --services core,admin-api,web-documentation \\
         --domain demo.baokim.vn --registry harbor.baokim.vn/b2b \\
         --outdir ./out

  3) File cau hinh (nhieu service, tuy chinh tung cai):
       python3 generate_k8s.py --config example-services.yaml --outdir ./out

LUU Y BAO MAT: cac mau ConfigMap/Secret chi sinh KHUNG (ten bien, gia tri
rong), khong bao gio nhung san mat khau / private key / API key that.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import yaml  # PyYAML - chi can khi doc --config dang .yaml
except ImportError:
    yaml = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")

PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


# --------------------------------------------------------------------------
# Doc & render template
# --------------------------------------------------------------------------

def load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render(template_text: str, values: dict) -> str:
    """Thay {{KEY}} bang values[KEY]. Neu thieu key -> bao loi ro rang."""
    def _sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"Thieu gia tri cho placeholder {{{{{key}}}}}")
        return str(values[key])
    return PLACEHOLDER_RE.sub(_sub, template_text)


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class ServiceSpec:
    name: str
    project: str
    image_tag: str = "latest"
    port: int = 80
    replicas_min: int = 1
    replicas_max: int = 2
    cpu_request: str = "200m"
    mem_request: str = "256Mi"
    mem_limit: str = "1Gi"
    needs_logs_volume: bool = False
    enable_autoscale: bool = True
    domain: str = "demo.baokim.vn"
    registry: str = "harbor.baokim.vn/b2b"
    namespace: Optional[str] = None
    extra_env_keys: List[str] = field(default_factory=list)

    @property
    def app_name(self) -> str:
        return f"{self.project}-{self.name}"

    @property
    def svc_name(self) -> str:
        return f"{self.app_name}-svc"

    @property
    def configmap_name(self) -> str:
        return f"env-{self.app_name}"

    @property
    def image(self) -> str:
        return f"{self.registry}/{self.app_name}:{self.image_tag}"

    @property
    def host(self) -> str:
        return f"{self.app_name}.{self.domain}"


DEFAULT_ENV_KEYS = [
    "APP_NAME", "APP_ENV", "APP_KEY", "APP_DEBUG", "APP_URL",
    "LOG_CHANNEL", "LOG_LEVEL",
    "DB_CONNECTION", "DB_HOST", "DB_PORT", "DB_DATABASE", "DB_USERNAME", "DB_PASSWORD",
    "CACHE_DRIVER", "QUEUE_CONNECTION", "SESSION_DRIVER", "SESSION_LIFETIME",
    "REDIS_HOST", "REDIS_PASSWORD", "REDIS_PORT",
    "TZ",
]


# --------------------------------------------------------------------------
# Render tung loai file tu template
# --------------------------------------------------------------------------

def render_deployment(svc: ServiceSpec) -> str:
    if svc.needs_logs_volume:
        volume_mounts = render(load_template("_volume_mounts.yaml.tpl"), {"APP_NAME": svc.app_name})
        volumes = render(load_template("_volumes.yaml.tpl"), {"APP_NAME": svc.app_name, "PROJECT": svc.project})
    else:
        volume_mounts = ""
        volumes = ""

    values = {
        "APP_NAME": svc.app_name,
        "IMAGE": svc.image,
        "MEM_REQUEST": svc.mem_request,
        "CPU_REQUEST": svc.cpu_request,
        "MEM_LIMIT": svc.mem_limit,
        "PORT": svc.port,
        "CONFIGMAP_NAME": svc.configmap_name,
        "VOLUME_MOUNTS": volume_mounts.rstrip("\n"),
        "VOLUMES": volumes.rstrip("\n"),
    }
    return render(load_template("deployment.yaml.tpl"), values)


def render_service(svc: ServiceSpec) -> str:
    return render(load_template("service.yaml.tpl"), {
        "SVC_NAME": svc.svc_name,
        "APP_NAME": svc.app_name,
    })


def render_hpa(svc: ServiceSpec) -> str:
    return render(load_template("hpa.yaml.tpl"), {
        "APP_NAME": svc.app_name,
        "REPLICAS_MIN": svc.replicas_min,
        "REPLICAS_MAX": svc.replicas_max,
    })


def render_configmap(svc: ServiceSpec) -> str:
    keys = DEFAULT_ENV_KEYS + svc.extra_env_keys
    lines = "\n".join(f'  {k}: ""  # TODO: dien gia tri' for k in keys)
    return render(load_template("configmap.yaml.tpl"), {
        "CONFIGMAP_NAME": svc.configmap_name,
        "ENV_KEYS": lines,
    })


def render_ingress(services: List[ServiceSpec]) -> str:
    rule_tpl = load_template("_ingress_rule.yaml.tpl")
    rules = [render(rule_tpl, {"HOST": svc.host, "SVC_NAME": svc.svc_name}).rstrip("\n")
             for svc in services]
    return render(load_template("ingress.yaml.tpl"), {
        "PROJECT": services[0].project,
        "INGRESS_RULES": "\n".join(rules),
    })


def render_pvc(project: str) -> str:
    return render(load_template("pvc.yaml.tpl"), {"PROJECT": project})


def render_secret() -> str:
    return load_template("secret.yaml.tpl")


# --------------------------------------------------------------------------
# Nhap lieu: tuong tac / dong lenh / file config
# --------------------------------------------------------------------------

def build_services_interactively() -> List[ServiceSpec]:
    print("=== Trinh sinh manifest Kubernetes (doc mau tu templates/) ===")
    project = input("Ten du an (vd: b2b): ").strip() or "b2b"
    raw_services = input(
        "Danh sach service, cach nhau boi dau phay (vd: core,admin-api): "
    ).strip()
    names = [s.strip() for s in raw_services.split(",") if s.strip()]
    if not names:
        print("Ban chua nhap service nao, thoat.")
        sys.exit(1)

    services = []
    for name in names:
        services.append(ServiceSpec(
            name=name, project=project,
            registry=f"harbor.baokim.vn/{project}"
        ))
    return services


def build_services_from_args(args) -> List[ServiceSpec]:
    names = [s.strip() for s in args.services.split(",") if s.strip()]
    if not names:
        print("Loi: --services rong.", file=sys.stderr)
        sys.exit(1)
    return [
        ServiceSpec(
            name=name, project=args.project, image_tag=args.image_tag,
            domain=args.domain, registry=args.registry, namespace=args.namespace,
            needs_logs_volume=args.with_logs_pvc, enable_autoscale=not args.no_hpa,
        )
        for name in names
    ]


def build_services_from_config(path: str) -> List[ServiceSpec]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            print("Can cai pyyaml: pip install pyyaml --break-system-packages", file=sys.stderr)
            sys.exit(1)
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    project = data.get("project", "b2b")
    domain = data.get("domain", "demo.baokim.vn")
    registry = data.get("registry", f"harbor.baokim.vn/{project}")
    namespace = data.get("namespace")

    services = []
    for item in data.get("services", []):
        services.append(ServiceSpec(
            name=item["name"], project=project,
            image_tag=item.get("image_tag", "latest"),
            port=item.get("port", 80),
            replicas_min=item.get("replicas_min", 1),
            replicas_max=item.get("replicas_max", 2),
            cpu_request=item.get("cpu_request", "200m"),
            mem_request=item.get("mem_request", "256Mi"),
            mem_limit=item.get("mem_limit", "1Gi"),
            needs_logs_volume=item.get("needs_logs_volume", False),
            enable_autoscale=item.get("enable_autoscale", True),
            domain=item.get("domain", domain),
            registry=item.get("registry", registry),
            namespace=item.get("namespace", namespace),
            extra_env_keys=item.get("extra_env_keys", []),
        ))
    return services


# --------------------------------------------------------------------------
# Ghi file
# --------------------------------------------------------------------------

def write_all(services: List[ServiceSpec], outdir: str):
    os.makedirs(outdir, exist_ok=True)

    configmap_parts = []
    service_parts = []
    hpa_parts = []

    for svc in services:
        # Write separate deployment file for each service, using the naming convention {app_name}.yaml
        _write(outdir, f"{svc.app_name}.yaml", render_deployment(svc))

        # Collect other manifests to combine
        configmap_parts.append(render_configmap(svc).strip())
        service_parts.append(render_service(svc).strip())
        if svc.enable_autoscale:
            hpa_parts.append(render_hpa(svc).strip())

    # Write combined configmap.yaml
    if configmap_parts:
        _write(outdir, "configmap.yaml", "\n---\n".join(configmap_parts) + "\n")

    # Write combined service.yaml
    if service_parts:
        _write(outdir, "service.yaml", "\n---\n".join(service_parts) + "\n")

    # Write combined autoscale.yaml
    if hpa_parts:
        _write(outdir, "autoscale.yaml", "\n---\n".join(hpa_parts) + "\n")

    _write(outdir, "ingress.yaml", render_ingress(services))
    _write(outdir, "pvc.yaml", render_pvc(services[0].project))
    _write(outdir, "secret.yaml", render_secret())

    print(f"\nDa sinh {len(services)} service vao thu muc: {outdir}")
    for fn in sorted(os.listdir(outdir)):
        print(f"  - {fn}")


def _write(outdir: str, filename: str, content: str):
    with open(os.path.join(outdir, filename), "w", encoding="utf-8") as f:
        f.write(content)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sinh manifest Kubernetes tu thu muc templates/")
    parser.add_argument("--project", help="Ten du an, vd: b2b")
    parser.add_argument("--services", help="Danh sach service, cach nhau boi dau phay")
    parser.add_argument("--domain", default="demo.baokim.vn")
    parser.add_argument("--registry", help="vd: harbor.baokim.vn/b2b")
    parser.add_argument("--namespace")
    parser.add_argument("--image-tag", default="latest")
    parser.add_argument("--with-logs-pvc", action="store_true")
    parser.add_argument("--no-hpa", action="store_true")
    parser.add_argument("--config", help="File JSON/YAML mo ta nhieu service")
    parser.add_argument("--outdir", help="Thu muc xuat file (mac dinh lay theo ten du an)")
    args = parser.parse_args()

    if args.config:
        services = build_services_from_config(args.config)
    elif args.project and args.services:
        services = build_services_from_args(args)
    else:
        services = build_services_interactively()

    outdir = args.outdir
    if not outdir:
        if services:
            outdir = f"./{services[0].project}"
        else:
            outdir = "./k8s-out"

    write_all(services, outdir)


if __name__ == "__main__":
    main()
